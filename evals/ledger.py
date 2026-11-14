"""Crash-persistent, process-serialized reservations. Uncertain calls keep their full hold."""
import json
import sqlite3
from decimal import Decimal, ROUND_CEILING
from pathlib import Path

from .budget import money
from .integrity import canonical, fingerprint, require


def micros(value):
    return int((money(value) * 1000000).to_integral_value(rounding=ROUND_CEILING))


class Ledger:
    def __init__(self, path, cap_usd, configuration):
        self.path = Path(path)
        require(not self.path.is_symlink(), "Ledger cannot be a symlink")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(str(self.path), timeout=10, isolation_level=None)
        self.connection.execute('PRAGMA synchronous=FULL')
        self.connection.execute('CREATE TABLE IF NOT EXISTS policy (id INTEGER PRIMARY KEY, cap INTEGER, fingerprint TEXT)')
        self.connection.execute('CREATE TABLE IF NOT EXISTS attempts (id TEXT PRIMARY KEY, request_hash TEXT, held INTEGER, actual INTEGER, state TEXT, metadata TEXT)')
        self.configuration = fingerprint(configuration)
        self.connection.execute('BEGIN IMMEDIATE')
        try:
            row = self.connection.execute('SELECT cap,fingerprint FROM policy WHERE id=1').fetchone()
            expected = (micros(cap_usd), self.configuration)
            require(row is None or row == expected, "Ledger budget/configuration cannot be reset")
            if row is None:
                self.connection.execute('INSERT INTO policy VALUES (1,?,?)', expected)
            self.connection.commit()
        except Exception:
            self.connection.rollback(); self.connection.close(); raise

    def close(self):
        self.connection.close()

    def reserve(self, attempt_id, request, maximum_usd):
        held = micros(maximum_usd)
        self.connection.execute('BEGIN IMMEDIATE')
        try:
            cap = self.connection.execute('SELECT cap FROM policy').fetchone()[0]
            require(self.connection.execute("SELECT COUNT(*) FROM attempts WHERE state='overrun'").fetchone()[0] == 0,
                    "Previous accounting overrun blocks dispatch")
            require(self.connection.execute('SELECT COUNT(*) FROM attempts').fetchone()[0] < 56,
                    "Attempt limit reached")
            committed = self.connection.execute('SELECT COALESCE(SUM(COALESCE(actual,held)),0) FROM attempts').fetchone()[0]
            require(committed + held <= cap, "Spending cap blocks dispatch")
            self.connection.execute('INSERT INTO attempts VALUES (?,?,?,NULL,?,?)',
                                    (attempt_id, fingerprint(request), held, 'reserved', '{}'))
            self.connection.commit()
        except Exception:
            self.connection.rollback(); raise

    def settle(self, attempt_id, actual_usd, metadata):
        actual = micros(actual_usd)
        self.connection.execute('BEGIN IMMEDIATE')
        try:
            row = self.connection.execute('SELECT held,actual FROM attempts WHERE id=?', (attempt_id,)).fetchone()
            require(row is not None and row[1] is None, "Missing/already reconciled reservation")
            # If provider accounting violates the bound, retain the overspend and freeze later dispatch.
            self.connection.execute('UPDATE attempts SET actual=?,state=?,metadata=? WHERE id=?',
                                    (actual, 'settled' if actual <= row[0] else 'overrun', canonical(metadata), attempt_id))
            self.connection.commit()
            require(actual <= row[0], "Actual cost exceeded reservation; stop")
        except Exception:
            if self.connection.in_transaction: self.connection.rollback()
            raise

    def uncertain(self, attempt_id):
        self.connection.execute("UPDATE attempts SET state='uncertain' WHERE id=? AND actual IS NULL", (attempt_id,))

    def snapshot(self):
        rows = self.connection.execute('SELECT id,request_hash,held,actual,state,metadata FROM attempts ORDER BY id').fetchall()
        return [{'attempt_id': r[0], 'request_sha256': r[1], 'reserved_microusd': r[2],
                 'actual_microusd': r[3], 'state': r[4], 'metadata': json.loads(r[5])} for r in rows]

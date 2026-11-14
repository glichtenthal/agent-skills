"""Shared retained-input/source and inventory utilities; no execution or grading."""
import shutil
from pathlib import Path
from .integrity import digest, local_file, object_json, require


def freeze_inputs(bundle, output, runtime_metadata, repository):
    for name in ['source-manifest.json', *bundle['manifest']['files']]:
        dest = output / 'inputs' / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(bundle['root'] / name, dest)
    for name in runtime_metadata['code_sha256']:
        dest = output / 'runtime-source' / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(repository / name, dest)


def inventory(root):
    return {str(p.relative_to(root)): digest(p.read_bytes()) for p in sorted(root.rglob('*'))
            if p.is_file() and p != root / 'hashes.json'}


def verify_inventory(root):
    root = Path(root).resolve()
    hashes = object_json(local_file(root, 'hashes.json'))
    require(set(hashes) == {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()
                            and p != root / 'hashes.json'}, 'Evidence inventory mismatch')
    for name, expected in hashes.items():
        require(digest(local_file(root, name).read_bytes()) == expected, 'Evidence hash mismatch: ' + name)
    return hashes

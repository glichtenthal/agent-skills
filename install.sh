#!/usr/bin/env bash

set -euo pipefail

all_skills=(briefing-room ground-truth the-quorum test-drive)
selected_skills=()
destination="${HOME}/.agents/skills"
update=false
dry_run=false
active_work_dir=''
active_stage_dir=''

usage() {
  cat <<'EOF'
Install the Judgment Infrastructure skill suite for Codex.

Usage:
  bash install.sh [options]

Options:
  --target codex          Install in ~/.agents/skills (default)
  --target legacy-codex   Install in ~/.codex/skills
  --dest PATH             Install in a custom skills directory
  --skill NAME            Install one skill; may be repeated
  --update                Replace existing copies with the pinned releases
  --dry-run               Show what would change without downloading or writing
  -h, --help              Show this help

Skills:
  briefing-room, ground-truth, the-quorum, test-drive
EOF
}

fail() {
  printf 'Error: %s\n' "$*" >&2
  exit 1
}

cleanup() {
  if [ -n "$active_stage_dir" ] && [ -e "$active_stage_dir" ]; then
    rm -rf "$active_stage_dir"
  fi
  if [ -n "$active_work_dir" ] && [ -d "$active_work_dir" ]; then
    rm -rf "$active_work_dir"
  fi
}

trap cleanup EXIT HUP INT TERM

skill_ref() {
  case "$1" in
    briefing-room) printf '%s\n' 'v1.2' ;;
    ground-truth) printf '%s\n' 'v1.2' ;;
    the-quorum) printf '%s\n' 'v1.3' ;;
    test-drive) printf '%s\n' 'v1.6' ;;
    *) return 1 ;;
  esac
}

is_known_skill() {
  skill_ref "$1" >/dev/null 2>&1
}

add_skill() {
  local requested="$1"
  local existing

  is_known_skill "$requested" || fail "Unknown skill '$requested'."
  for existing in "${selected_skills[@]}"; do
    [ "$existing" = "$requested" ] && return
  done
  selected_skills+=("$requested")
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --target)
      [ "$#" -ge 2 ] || fail "--target requires a value."
      case "$2" in
        codex) destination="${HOME}/.agents/skills" ;;
        legacy-codex) destination="${HOME}/.codex/skills" ;;
        *) fail "Unsupported target '$2'. Use codex or legacy-codex." ;;
      esac
      shift 2
      ;;
    --dest)
      [ "$#" -ge 2 ] || fail "--dest requires a path."
      destination="$2"
      shift 2
      ;;
    --skill)
      [ "$#" -ge 2 ] || fail "--skill requires a name."
      add_skill "$2"
      shift 2
      ;;
    --update)
      update=true
      shift
      ;;
    --dry-run)
      dry_run=true
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      fail "Unknown option '$1'."
      ;;
  esac
done

if [ "${#selected_skills[@]}" -eq 0 ]; then
  selected_skills=("${all_skills[@]}")
fi

if [ "$dry_run" = false ]; then
  command -v curl >/dev/null 2>&1 || fail "curl is required."
  command -v unzip >/dev/null 2>&1 || fail "unzip is required."
  mkdir -p "$destination"
fi

printf 'Destination: %s\n' "$destination"

for skill_name in "${selected_skills[@]}"; do
  release_ref="$(skill_ref "$skill_name")"
  target_dir="${destination%/}/$skill_name"
  release_url="https://github.com/glichtenthal/$skill_name/releases/download/$release_ref/$skill_name.skill"

  if [ -e "$target_dir" ] && [ "$update" = false ]; then
    printf 'Skipping %s: already installed (use --update to replace it).\n' "$skill_name"
    continue
  fi

  if [ "$dry_run" = true ]; then
    action='Install'
    [ -e "$target_dir" ] && action='Update'
    printf '%s %s %s at %s\n' "$action" "$skill_name" "$release_ref" "$target_dir"
    continue
  fi

  work_dir="$(mktemp -d "${TMPDIR:-/tmp}/judgment-infrastructure.XXXXXX")"
  archive_path="$work_dir/$skill_name.skill"
  unpack_dir="$work_dir/unpacked"
  stage_dir="${destination%/}/.$skill_name.install.$$"
  previous_dir="$work_dir/previous-$skill_name"
  active_work_dir="$work_dir"
  active_stage_dir="$stage_dir"

  mkdir -p "$unpack_dir"
  curl -fsSL --retry 3 --retry-delay 1 "$release_url" -o "$archive_path"

  while IFS= read -r archive_entry; do
    case "$archive_entry" in
      "$skill_name"|"$skill_name/"|"$skill_name/"*) ;;
      *) fail "Unexpected path in $skill_name release: $archive_entry" ;;
    esac
  done < <(unzip -Z1 "$archive_path")

  unzip -q "$archive_path" -d "$unpack_dir"
  source_dir="$unpack_dir/$skill_name"
  [ -f "$source_dir/SKILL.md" ] || fail "$skill_name release is missing SKILL.md."
  grep -Eq "^name:[[:space:]]*$skill_name[[:space:]]*$" "$source_dir/SKILL.md" || \
    fail "$skill_name release has an unexpected skill name."
  [ ! -e "$stage_dir" ] || fail "Temporary install path already exists: $stage_dir"

  mv "$source_dir" "$stage_dir"
  if [ -e "$target_dir" ]; then
    mv "$target_dir" "$previous_dir"
    if ! mv "$stage_dir" "$target_dir"; then
      mv "$previous_dir" "$target_dir"
      fail "Could not update $skill_name; the previous copy was restored."
    fi
    printf 'Updated %s to %s.\n' "$skill_name" "$release_ref"
  else
    mv "$stage_dir" "$target_dir"
    printf 'Installed %s %s.\n' "$skill_name" "$release_ref"
  fi

  rm -rf "$work_dir"
  active_work_dir=''
  active_stage_dir=''
done

printf 'Done.\n'

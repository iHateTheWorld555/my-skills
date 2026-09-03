#!/bin/sh
set -eu

PACK_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
BIN_DIR=${DOCDEV_BIN_DIR:-"$HOME/.local/bin"}
SKILL_DIR=${CLAUDE_SKILLS_DIR:-"$HOME/.claude/skills"}
BIN_TARGET="$BIN_DIR/docdev"
SKILL_TARGET="$SKILL_DIR/doc-driven-dev-v3"

if [ "${1:-}" = "--dry-run" ]; then
  printf 'cli: %s -> %s\n' "$BIN_TARGET" "$PACK_DIR/bin/docdev"
  printf 'skill: %s -> %s\n' "$SKILL_TARGET" "$PACK_DIR"
  exit 0
fi

command -v python3 >/dev/null 2>&1 || {
  printf 'python3 is required\n' >&2
  exit 1
}

mkdir -p "$BIN_DIR" "$SKILL_DIR"

if [ -e "$BIN_TARGET" ] && [ ! -L "$BIN_TARGET" ]; then
  printf 'refusing to replace non-symlink: %s\n' "$BIN_TARGET" >&2
  exit 1
fi
if [ -e "$SKILL_TARGET" ] && [ ! -L "$SKILL_TARGET" ]; then
  printf 'refusing to replace non-symlink: %s\n' "$SKILL_TARGET" >&2
  exit 1
fi

ln -sfn "$PACK_DIR/bin/docdev" "$BIN_TARGET"
ln -sfn "$PACK_DIR" "$SKILL_TARGET"
printf 'installed docdev at %s\n' "$BIN_TARGET"
printf 'installed skill at %s\n' "$SKILL_TARGET"

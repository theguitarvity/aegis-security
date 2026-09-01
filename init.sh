#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
ENGINE_SRC="$SCRIPT_DIR/.agent/skills/aegis-security"
ENGINE_DST="$HOME/.aegis-security-engine"
MARKER_FILE="$ENGINE_DST/.managed-by-aegis-security-init"

log() { printf '[aegis-security init] %s\n' "$1"; }
die() { printf '[aegis-security init] ERROR: %s\n' "$1" >&2; exit 1; }

install_engine() {
  [ -f "$ENGINE_SRC/SKILL.md" ] || die "canonical skill not found at $ENGINE_SRC"
  mkdir -p "$ENGINE_DST"
  if command -v rsync >/dev/null 2>&1; then
    rsync -a --delete --exclude ".managed-by-aegis-security-init" "$ENGINE_SRC"/ "$ENGINE_DST"/
  else
    rm -rf "${ENGINE_DST:?}"/*
    cp -a "$ENGINE_SRC"/. "$ENGINE_DST"/
  fi
  printf 'installed from %s on %s\n' "$SCRIPT_DIR" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$MARKER_FILE"
  log "engine mirrored to $ENGINE_DST"
}

write_pointer() {
  local dest="$1"
  mkdir -p "$(dirname "$dest")"
  cat > "$dest" <<EOF
---
name: aegis-security
description: Run the Aegis local-first security validation harness and produce normalized findings, release gates, and SpecMaster remediation roadmaps.
---

# Aegis Security (global pointer)

Installed globally by init.sh. Read the canonical engine before acting:

    $ENGINE_DST/SKILL.md

Run:

    python3 $ENGINE_DST/scripts/doctor.py
    python3 $ENGINE_DST/scripts/scan.py --project . --profile quick

Aggressive profiles require explicit local/private target authorization and
bounded execution. Aegis recommends; it does not remediate unless delegated.
EOF
  log "installed $dest"
}

install_globals() {
  write_pointer "$HOME/.codex/skills/aegis-security/SKILL.md"
  write_pointer "$HOME/.agents/skills/aegis-security/SKILL.md"
  write_pointer "$HOME/.copilot/skills/aegis-security/SKILL.md"
  write_pointer "$HOME/.claude/skills/aegis-security/SKILL.md"
  mkdir -p "$HOME/.claude/commands"
  cat > "$HOME/.claude/commands/aegis-security.md" <<EOF
---
description: "Run Aegis Security local-first validation harness"
---

Read $ENGINE_DST/SKILL.md in full before acting. Default to profile quick.
Use python3 $ENGINE_DST/scripts/scan.py --project . --profile quick unless
the user requests another governed profile.
EOF
  log "installed $HOME/.claude/commands/aegis-security.md"
}

link_project() {
  local project_dir="${1:-$PWD}"
  project_dir="$(cd -- "$project_dir" &>/dev/null && pwd)" || die "project path not found"
  mkdir -p "$project_dir/.agents/skills/aegis-security" "$project_dir/.github/skills/aegis-security"
  write_pointer "$project_dir/.agents/skills/aegis-security/SKILL.md"
  write_pointer "$project_dir/.github/skills/aegis-security/SKILL.md"
}

case "${1:-install}" in
  install)
    install_engine
    install_globals
    log "done. Use \$aegis-security or /aegis-security in any project."
    ;;
  link)
    shift
    link_project "${1:-$PWD}"
    ;;
  --engine-only)
    install_engine
    ;;
  -h|--help)
    sed -n '1,80p' "$0"
    ;;
  *)
    die "unknown argument: $1"
    ;;
esac

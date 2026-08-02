#!/usr/bin/env bash
# generate-diff.sh — Generate a diff for reviewer handoff with ancestor validation.
#
# Usage:
#   generate-diff.sh --ws WS4 --sprint 3 --base <sha> --head <sha> \
#                     [--worktree <path>]
#
# Generates the raw BASE..HEAD diff. Does NOT scope or filter — the
# reviewer sees everything, including shared-file changes from parallel
# work. The ancestor check is the only guardrail: it catches stale
# BASE_SHA before the base reaches the diff.
#
# NOTE: The output path OUT_DIR (default ".deep-plan/handoff") is
# relative to the current working directory — NOT the --worktree. Runs of
# the script with --worktree are resolved for git, but the diff still
# lands in the caller's cwd. If you want the artifacts beside the
# worktree, pass an absolute --out-dir or cd into the worktree first.

set -euo pipefail

WS=""
SPRINT=""
BASE=""
HEAD=""
WORKTREE=""
OUT_DIR=".deep-plan/handoff"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --ws|--ws-lane) WS="$2"; shift 2 ;;
    --sprint) SPRINT="$2"; shift 2 ;;
    --base) BASE="$2"; shift 2 ;;
    --head) HEAD="$2"; shift 2 ;;
    --worktree) WORKTREE="$2"; shift 2 ;;
    --out-dir) OUT_DIR="$2"; shift 2 ;;
    *) echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

if [[ ( -z "$WS" && -z "$SPRINT" ) || -z "$BASE" || -z "$HEAD" ]]; then
  echo "Usage: generate-diff.sh --sprint <m> [--ws-lane WS<n>] --base <sha> --head <sha> [--worktree <path>]" >&2
  exit 1
fi

if [[ -n "$SPRINT" && -n "$WS" ]]; then
  LABEL="Sprint${SPRINT}-${WS}"
elif [[ -n "$SPRINT" ]]; then
  LABEL="Sprint${SPRINT}"
else
  LABEL="${WS}"
fi

mkdir -p "$OUT_DIR"
DIFF_FILE="${OUT_DIR}/${LABEL}-diff.diff"

run_git() {
  if [[ -n "$WORKTREE" ]]; then
    git -C "$WORKTREE" "$@"
  else
    git "$@"
  fi
}

# BASE must be an ancestor of HEAD. If not, BASE_SHA was captured at the
# wrong point (e.g. after parallel commits already landed). Stop here —
# a diff from a non-ancestor base is meaningless.
if ! run_git merge-base --is-ancestor "$BASE" "$HEAD" 2>/dev/null; then
  echo "ERROR: $BASE is not an ancestor of $HEAD in $(run_git rev-parse --show-toplevel)." >&2
  echo "BASE_SHA was captured at the wrong point, or commits landed between" >&2
  echo "BASE and HEAD. Re-derive the correct base before diffing." >&2
  exit 1
fi

{
  echo "# ${LABEL} diff (${BASE}..${HEAD})"
  echo "# generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo
  echo "## Commits"
  run_git log --oneline "${BASE}..${HEAD}"
  echo
  echo "## Stat"
  run_git diff --stat "${BASE}..${HEAD}"
  echo
  echo "## Full diff"
  run_git diff "${BASE}..${HEAD}"
} > "$DIFF_FILE"

echo "Wrote $DIFF_FILE"

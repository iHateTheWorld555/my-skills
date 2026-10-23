#!/usr/bin/env bash
# ralph.sh -- fixed-point loop driver for citation-bfs-survey.
#
# Re-invokes a FRESH agent process each iteration. The agent cannot early-stop
# because it does not own the loop: paperq gate does. Loop exits only when gate
# returns exit code 3 (survey complete) or the hard iteration cap is hit.
#
#   ./ralph.sh --outdir survey [--max-iters 30] [--batch 4] [--agent "claude -p"]
set -uo pipefail

OUTDIR="survey"; MAX_ITERS=30; BATCH=4
AGENT="${RALPH_AGENT:-claude -p --dangerously-skip-permissions}"
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --outdir)    OUTDIR="$2"; shift 2 ;;
    --max-iters) MAX_ITERS="$2"; shift 2 ;;
    --batch)     BATCH="$2"; shift 2 ;;
    --agent)     AGENT="$2"; shift 2 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

PQ="$SKILL_DIR/scripts/paperq.py"
PY="$(command -v python3)"
LOG="$OUTDIR/ralph.log"
mkdir -p "$OUTDIR"

if [[ ! -f "$OUTDIR/paperq.sqlite" ]]; then
  echo "[ralph] no survey at $OUTDIR -- run 'paperq.py init' + 'seed' first." >&2
  exit 2
fi

say() { echo "[ralph $(date +%H:%M:%S)] $*" | tee -a "$LOG"; }
say "start: outdir=$OUTDIR max_iters=$MAX_ITERS batch=$BATCH"

for ((i=1; i<=MAX_ITERS; i++)); do
  GATE="$("$PY" "$PQ" --outdir "$OUTDIR" gate --batch "$BATCH")"; RC=$?
  echo "$GATE" >> "$LOG"

  if [[ $RC -eq 3 ]]; then
    say "iter $i: gate says DONE"
    "$PY" "$PQ" --outdir "$OUTDIR" report --out survey.md | tee -a "$LOG"
    say "finished after $i iterations"
    exit 0
  fi
  if [[ $RC -ne 0 ]]; then
    say "gate failed rc=$RC -- aborting"; exit 1
  fi

  say "iter $i/$MAX_ITERS: $(echo "$GATE" | grep -o '"next_action":.*' | head -1)"

  PROMPT=$(cat <<EOF
Use the citation-bfs-survey skill. Working dir for the survey: $OUTDIR

You are ONE iteration of an external loop. Do NOT try to finish the whole
survey, and do NOT decide whether the survey is complete -- an external gate
decides that. Your job is to advance the queue as much as you can this turn,
then stop.

Current gate state:
$GATE

Do exactly this:
1. Triage every candidate (accept --why / reject) if any exist.
2. Claim a batch of frontier papers ($BATCH) and process them IN PARALLEL with
   sub-agents: one sub-agent per paper. Each sub-agent must expand the paper,
   triage its candidates, and record it with a substantive summary.
3. Run more seed queries from new angles if the gate asks for it, using
   --sources arxiv,crossref,gscholar (multiple engines: their blind spots
   are structural, not random).
4. If any engine/backend reports silent or degraded, run \`probe\` before
   treating the absence of results as real.
5. Do not write the final report. Do not say the survey is done.
EOF
)
  if ! echo "$PROMPT" | eval "$AGENT" >>"$LOG" 2>&1; then
    say "iter $i: agent exited non-zero (continuing; gate is authoritative)"
  fi
done

say "hit max-iters=$MAX_ITERS without gate DONE -- inspect: $PQ --outdir $OUTDIR status"
exit 4

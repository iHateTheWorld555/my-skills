# Running a dream on a schedule

Choose one of three; all of them run the same skill.

## 1. In-session recurrence

While a session is open, ask for a recurring dream (the `/loop` skill or the scheduler). Suits a machine that stays logged in. Nothing survives the session ending.

## 2. System cron with a headless Claude Code run

```bash
# crontab -e — every night at 01:17, dreaming over the last 14 days.
17 1 * * * cd /path/to/project && /path/to/claude -p "run the dreaming skill for this project" >> ~/.claude/dreams/cron.log 2>&1
```

- Run it from the project directory: the exporter derives the transcript directory from the working directory.
- The state file skips sessions a previous night already covered, so a 14-day window is cheap.
- A failed night leaves the sessions uncommitted, so the next night takes them again.
- Use an API key in the environment or a logged-in profile, whichever the host already uses.
- Keep `>>` on the log; the skill's report is what tells you whether the night was complete.

## 3. One-off manual dream

```bash
python3 -I <SKILL_DIR>/scripts/export_sessions.py --since 60d
```

Then run the skill's Step 2–4 in an interactive session. Use this after a long gap: the default 14-day window would miss older sessions.

## Notes

- **Do not put a fixed `--since` on the cron line if you rely on the state file** — it is harmless for correctness (hashes decide), but it makes every night scan the same window.
- A session still being written is skipped by the exporter's 5-minute settle window; it is picked up the next night.
- The transcripts under `<store>/.dream/transcripts/` are full private copies. Delete old run directories if disk or secrecy matters.

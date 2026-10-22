# Bundled examples

Two tiny sample skills so you can see SkillVet work in 10 seconds —
no download of anything real required.

## clean-skill/ — expect 100/A, SAFE

A PDF summarizer that works only on files the user hands it and uploads
nothing anywhere.

```bash
python3 ../skillvet.py clean-skill
```

## evil-skill/ — expect 0/F, DANGEROUS

**Do not install this skill in a real agent.** It is a teaching fixture:
its `SKILL.md` instructs the agent to ignore its rules and hide telemetry
from the user, and its `scripts/setup.py` reads an API key and an SSH key,
posts them to a drop endpoint, installs a cron job, and runs a
`curl | sh` payload. Every line exists to trip specific rules — compare
the scanner output against [docs/RULES.md](../docs/RULES.md) to see which
rule caught what.

```bash
python3 ../skillvet.py evil-skill
```

> The exfiltration URL and payload IP in the fixture are non-routable
> documentation addresses (RFC 5737). The fixture is inert text unless a
> human deliberately executes it — don't.

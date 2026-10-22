# Security Policy

## Reporting a vulnerability

Found a way to make SkillVet miss something dangerous, crash on a crafted
input, or — worst of all — a pattern that makes SkillVet itself unsafe to
run on untrusted folders? Please report it privately via GitHub's
**Security → Report a vulnerability** on this repository instead of
opening a public issue.

You can expect an acknowledgement within 7 days.

## Scope notes

- SkillVet only *reads* the files it scans; it never executes them.
- Bypassing a detection rule is a legitimate research contribution —
  send it as a private report first if the bypass is novel, then we'd
  love a public write-up once a rule fix ships.

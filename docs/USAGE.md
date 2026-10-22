# SkillVet Usage Guide

## Contents
- [Installation](#installation)
- [Basic scanning](#basic-scanning)
- [Reading the report](#reading-the-report)
- [JSON output](#json-output)
- [CI integration](#ci-integration)
- [Scanning MCP configs](#scanning-mcp-configs)
- [Bulk-scanning a skills library](#bulk-scanning-a-skills-library)

## Installation

SkillVet is one Python file (3.9+, standard library only). No pip install,
no virtualenv, nothing to phone home.

```bash
# Option 1 — download the single file
curl -O https://raw.githubusercontent.com/08raviyadav/skillvet/main/skillvet.py
chmod +x skillvet.py

# Option 2 — clone the repo (gets examples + tests too)
git clone https://github.com/08raviyadav/skillvet.git
```

Verify it works:

```bash
python3 skillvet.py --list-rules     # prints all 27 rules
python3 skillvet.py --version
```

## Basic scanning

```bash
python3 skillvet.py ./downloaded-skill        # a folder
python3 skillvet.py ./SKILL.md                # a single file
python3 skillvet.py ./mcp-config.json         # an MCP config
```

Scanned file types: `.md .txt .py .sh .bash .js .ts .json .yaml .yml .toml .ps1`.
`.git`, `node_modules`, and virtualenv folders are skipped automatically.

## Reading the report

```
Score: 82/100   Grade: B   Verdict: LOW RISK
```

| Score | Grade | Verdict | Meaning |
|---|---|---|---|
| 90–100 | A | SAFE | No or negligible red flags |
| 75–89 | B | LOW RISK | Minor flags; skim the findings |
| 60–74 | C | CAUTION | Read every finding before installing |
| 40–59 | D | RISKY | Serious flags; install only if you fully understand them |
| 0–39 | F | DANGEROUS | Do not install without a line-by-line audit |

Each finding shows severity, file, line number, the offending text, and a
plain-language explanation. Findings are grouped by category.

**The number is a triage tool, not a verdict on the author.** A B-grade
skill with one explained API-key read can be safer than an A-grade skill
doing something novel the rules don't know yet. Always read the findings.

## JSON output

```bash
python3 skillvet.py ./skill --json report.json
```

```json
{
  "target": "./skill",
  "files_scanned": 3,
  "score": 82,
  "grade": "B",
  "verdict": "LOW RISK",
  "findings": [
    {
      "rule": "SECRET-03",
      "category": "Secret access",
      "severity": "high",
      "file": "./skill/scripts/run.py",
      "line": 12,
      "excerpt": "key = os.environ[\"OPENAI_API_KEY\"]",
      "why": "Pulls an API key / token / secret straight from the environment."
    }
  ]
}
```

## CI integration

SkillVet exits `1` when the score falls below `--fail-under` (default 60):

```bash
python3 skillvet.py ./skills --fail-under 75   # stricter gate
echo $?   # 0 = pass, 1 = below threshold, 2 = bad path
```

**GitHub Actions (using the bundled action):**

```yaml
name: Vet skills
on: [pull_request]
jobs:
  skillvet:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: 08raviyadav/skillvet@v1
        with:
          path: ./skills
          fail-under: "60"
```

**Any other CI / local shell:**

```yaml
# e.g. GitLab CI, Jenkins, a Makefile — same pattern everywhere
script:
  - curl -sO https://raw.githubusercontent.com/08raviyadav/skillvet/main/skillvet.py
  - python3 skillvet.py ./skills --fail-under 60
```

**Pre-commit hook** (`.git/hooks/pre-commit`):

```bash
#!/bin/sh
# Vet any staged skill folders before they land in the repo
python3 skillvet.py ./skills --fail-under 60 || {
  echo "SkillVet blocked this commit. Review the findings above."
  exit 1
}
```

## Scanning MCP configs

MCP server configs (`mcp.json`, `.mcp.json`, `claude_desktop_config.json`,
etc.) are JSON — SkillVet scans them like any other file. Point it at the
config or the folder containing it. Rules that commonly fire on bad MCP
configs: SHELL-01/04 (command execution in server launch commands),
SECRET-02/03 (env blocks carrying keys), NET-02 (raw-IP server endpoints).

## Bulk-scanning a skills library

```bash
for d in ~/skills/*/; do
  echo "== $d"
  python3 skillvet.py "$d" | grep -E "Score:|Verdict:"
done
```

Or generate one JSON per skill and aggregate with `jq`:

```bash
for d in ~/skills/*/; do
  python3 skillvet.py "$d" --json "reports/$(basename "$d").json" >/dev/null
done
jq -s 'map({skill: .target, score: .score, grade: .grade})
       | sort_by(.score)' reports/*.json
```

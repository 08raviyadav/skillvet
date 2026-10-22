#!/usr/bin/env python3
"""
SkillVet — security scanner for AI agent skills, MCP configs, and agent
instruction files.

Agent skills (SKILL.md), MCP server configs, and similar instruction packs
can tell an AI agent to run shell commands, read your secrets, or quietly
ignore you. SkillVet statically scans them BEFORE you install, and gives a
score, a grade, and line-by-line findings.

Zero dependencies. Python 3.9+. One file.

    python3 skillvet.py <path-to-skill-folder-or-file>
    python3 skillvet.py ./skills --json report.json
    python3 skillvet.py ./skills --fail-under 60   # CI exit code

Exit code: 0 when the worst score >= --fail-under (default 60), else 1.
"""

import argparse
import json
import os
import re
import sys

VERSION = "0.1.0"

# ---------------------------------------------------------------- rules
# Each rule: (id, category, severity, compiled regex, why it matters)
# severity weights: critical 25, high 15, medium 8, low 3

SEVERITY_WEIGHT = {"critical": 25, "high": 15, "medium": 8, "low": 3}

RAW_RULES = [
    # --- instruction manipulation: the skill talks the agent into misbehaving
    ("MANIP-01", "Instruction manipulation", "critical",
     r"ignore (all )?(previous|prior|above) instructions",
     "Tells the agent to ignore its instructions — classic prompt-injection bait."),
    ("MANIP-02", "Instruction manipulation", "critical",
     r"(do not|don'?t|never) (tell|inform|notify|mention to) the user",
     "Instructs the agent to hide its behaviour from the user."),
    ("MANIP-03", "Instruction manipulation", "critical",
     r"(act as if|pretend) you (have no|don'?t have) (restrictions|rules|limits)",
     "Asks the agent to pretend its safety rules do not exist."),
    ("MANIP-04", "Instruction manipulation", "high",
     r"without (asking|telling|notifying) (the user|permission|approval)",
     "Authorizes silent action without the user's knowledge or consent."),
    ("MANIP-05", "Instruction manipulation", "high",
     r"(secretly|silently|quietly) (send|upload|post|exfiltrate|collect)",
     "Covert data collection language."),

    # --- secret access
    ("SECRET-01", "Secret access", "critical",
     r"(\.ssh[/\\]|id_rsa|id_ed25519|\.aws[/\\]credentials|\.gnupg)",
     "Touches SSH keys or cloud credential stores."),
    ("SECRET-02", "Secret access", "high",
     r"(open|read|cat|load|parse)\s*\(?\s*['\"~./\w-]*\.env\b",
     "Reads a .env file — where API keys and tokens live."),
    ("SECRET-03", "Secret access", "high",
     r"os\.environ\[?\s*['\"][A-Z_]*(KEY|TOKEN|SECRET|PASSWORD)['\"]",
     "Pulls an API key / token / secret straight from the environment."),
    ("SECRET-04", "Secret access", "high",
     r"(ask|prompt|request) the user for (their |his |her )?(password|api key|token|credentials)",
     "Asks the user to hand over a password, key, or token."),
    ("SECRET-05", "Secret access", "medium",
     r"(keychain|credential manager|vault) (read|access|dump|extract)",
     "Reaches into the OS credential store."),

    # --- shell execution
    ("SHELL-01", "Shell execution", "high",
     r"(subprocess\.(run|Popen|call|check_output)|os\.system\s*\()",
     "Runs shell commands via Python subprocess / os.system."),
    ("SHELL-02", "Shell execution", "critical",
     r"(curl|wget)\s[^|]*\|\s*(sudo\s+)?(sh|bash|zsh|python)",
     "Pipes a remote download straight into an interpreter (curl | sh)."),
    ("SHELL-03", "Shell execution", "high",
     r"\b(eval|exec)\s*\(",
     "Dynamic eval/exec — runs code that static review cannot see."),
    ("SHELL-04", "Shell execution", "high",
     r"child_process\.(exec|execSync|spawn)|os/exec|Runtime\.getRuntime\(\)\.exec",
     "Runs shell commands from JS/Java/Go code."),
    ("SHELL-05", "Shell execution", "medium",
     r"powershell\s+(-enc|/enc|enc\s)",
     "Encoded PowerShell — a common hiding place for payloads."),

    # --- network exfiltration
    ("NET-01", "Network exfiltration", "critical",
     r"(webhook\.site|requestbin|pastebin\.com|transfer\.sh|file\.io|anonfiles)",
     "Known drop / paste services used to exfiltrate data."),
    ("NET-02", "Network exfiltration", "high",
     r"https?://\d{1,3}(\.\d{1,3}){3}(:\d+)?/",
     "Hard-coded raw IP endpoint — no domain to audit or block."),
    ("NET-03", "Network exfiltration", "medium",
     r"(requests|httpx|urllib|fetch|axios)\.(post|request|put)\s*\(",
     "Outbound POST from bundled code — check what it sends and where."),
    ("NET-04", "Network exfiltration", "medium",
     r"socket\.(socket|create_connection)|net\.connect\s*\(",
     "Raw socket use — bypasses HTTP-level logging and proxies."),

    # --- persistence & system modification
    ("PERSIST-01", "Persistence", "high",
     r"(crontab|systemd|launchctl|LaunchAgents|schtasks|Startup folder)",
     "Installs persistence (cron / services / startup items)."),
    ("PERSIST-02", "Persistence", "medium",
     r"(\.bashrc|\.zshrc|\.profile|registry.*\\Run\b|CurrentVersion\\Run)",
     "Modifies shell profiles or OS auto-run locations."),
    ("PERSIST-03", "Persistence", "medium",
     r"chmod\s+777|chmod\s+\+x\s+.*&&|\bsudo\b",
     "Loose permissions or sudo use."),

    # --- obfuscation
    ("OBF-01", "Obfuscation", "high",
     r"[A-Za-z0-9+/]{120,}={0,2}",
     "Long base64-looking blob — content a reviewer cannot read at a glance."),
    ("OBF-02", "Obfuscation", "medium",
     r"(\\x[0-9a-fA-F]{2}){6,}",
     "Hex-escaped string — often hides commands or URLs."),
    ("OBF-03", "Obfuscation", "medium",
     r"base64\s*(-d|--decode)|b64decode|atob\s*\(",
     "Decodes base64 at runtime — ask what it decodes and why."),

    # --- broad permissions
    ("PERM-01", "Broad permissions", "medium",
     r"(--no-sandbox|disable.*(security|sandbox|firewall)|allow.*all.*(origins|hosts))",
     "Asks to switch off a security boundary."),
    ("PERM-02", "Broad permissions", "low",
     r"(full access|unrestricted access|any file on (the )?(system|disk|computer))",
     "Requests far broader access than a skill normally needs."),
]

RULES = [
    (rid, cat, sev, re.compile(pat, re.IGNORECASE), why)
    for (rid, cat, sev, pat, why) in RAW_RULES
]

SCAN_EXTENSIONS = {".md", ".txt", ".py", ".sh", ".bash", ".js", ".ts",
                   ".json", ".yaml", ".yml", ".toml", ".ps1"}
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv"}
MAX_FILE_BYTES = 2_000_000


def grade(score):
    if score >= 90:
        return "A"
    if score >= 75:
        return "B"
    if score >= 60:
        return "C"
    if score >= 40:
        return "D"
    return "F"


def verdict(score):
    if score >= 90:
        return "SAFE"
    if score >= 75:
        return "LOW RISK"
    if score >= 60:
        return "CAUTION"
    if score >= 40:
        return "RISKY"
    return "DANGEROUS"


def scan_file(path):
    findings = []
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            lines = fh.read().splitlines()
    except OSError:
        return findings
    for lineno, line in enumerate(lines, 1):
        for rid, cat, sev, rx, why in RULES:
            if rx.search(line):
                findings.append({
                    "rule": rid,
                    "category": cat,
                    "severity": sev,
                    "file": path,
                    "line": lineno,
                    "excerpt": line.strip()[:160],
                    "why": why,
                })
    return findings


def iter_targets(root):
    if os.path.isfile(root):
        yield root
        return
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in sorted(filenames):
            if os.path.splitext(name)[1].lower() in SCAN_EXTENSIONS:
                p = os.path.join(dirpath, name)
                if os.path.getsize(p) <= MAX_FILE_BYTES:
                    yield p


def scan(root):
    all_findings = []
    files = list(iter_targets(root))
    for f in files:
        all_findings.extend(scan_file(f))
    deduction = sum(SEVERITY_WEIGHT[f["severity"]] for f in all_findings)
    score = max(0, 100 - deduction)
    return {
        "target": root,
        "files_scanned": len(files),
        "score": score,
        "grade": grade(score),
        "verdict": verdict(score),
        "findings": all_findings,
    }


def print_report(result):
    r = result
    print(f"\nSkillVet report — {r['target']}")
    print("=" * 60)
    print(f"Files scanned: {r['files_scanned']}")
    print(f"Score: {r['score']}/100   Grade: {r['grade']}   Verdict: {r['verdict']}")
    if not r["findings"]:
        print("\nNo red flags found. (Static scan — see limitations in README.)")
        return
    by_cat = {}
    for f in r["findings"]:
        by_cat.setdefault(f["category"], []).append(f)
    for cat, items in by_cat.items():
        print(f"\n[{cat}] — {len(items)} finding(s)")
        for f in items:
            rel = os.path.basename(f["file"])
            print(f"  {f['severity'].upper():8} {rel}:{f['line']}  ({f['rule']})")
            print(f"           {f['excerpt']}")
            print(f"           → {f['why']}")
    print("\nReminder: a finding is a question to ask the author, not proof")
    print("of malice. Legitimate skills sometimes need shell or network access.")


def print_rules():
    print(f"SkillVet {VERSION} — {len(RULES)} rules")
    print("=" * 60)
    current = None
    for rid, cat, sev, _rx, why in RULES:
        if cat != current:
            current = cat
            print(f"\n[{cat}]")
        print(f"  {rid:11} {sev:8} {why}")
    print("\nFull reference: docs/RULES.md")


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="skillvet",
        description="Security scanner for AI agent skills & MCP configs.")
    ap.add_argument("path", nargs="?", help="Skill file or folder to scan")
    ap.add_argument("--json", metavar="FILE",
                    help="Also write a machine-readable JSON report")
    ap.add_argument("--fail-under", type=int, default=60,
                    help="Exit 1 if score falls below this (default 60)")
    ap.add_argument("--list-rules", action="store_true",
                    help="Print every detection rule and exit")
    ap.add_argument("--version", action="version",
                    version=f"skillvet {VERSION}")
    args = ap.parse_args(argv)

    if args.list_rules:
        print_rules()
        return 0

    if not args.path:
        ap.error("path is required (or use --list-rules)")

    if not os.path.exists(args.path):
        print(f"error: no such path: {args.path}", file=sys.stderr)
        return 2

    result = scan(args.path)
    print_report(result)

    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(result, fh, indent=2)
        print(f"\nJSON report written to {args.json}")

    return 0 if result["score"] >= args.fail_under else 1


if __name__ == "__main__":
    sys.exit(main())

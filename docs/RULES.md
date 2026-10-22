# SkillVet Rule Reference

Every rule in the scanner, what it catches, and why it matters.
Run `python3 skillvet.py --list-rules` for the same table in your terminal.

**Scoring:** each finding deducts points by severity — critical 25, high 15,
medium 8, low 3 — from 100. Grades: A ≥ 90, B ≥ 75, C ≥ 60, D ≥ 40, F < 40.

> A finding is a **question to ask the author**, not proof of malice.
> Legitimate skills sometimes need shell or network access. The point of
> SkillVet is that you see it *before* you install.

---

## Instruction manipulation

Skills talk directly to an agent. This category catches a skill talking the
agent into misbehaving — the prompt-injection layer no code scanner sees.

| ID | Severity | Detects |
|---|---|---|
| MANIP-01 | critical | "ignore previous/prior instructions" |
| MANIP-02 | critical | "do not tell / never inform the user" |
| MANIP-03 | critical | "act as if you have no restrictions/rules" |
| MANIP-04 | high | acting "without asking the user / without permission" |
| MANIP-05 | high | "secretly/silently send, upload, collect…" |

**False-positive note:** security documentation *about* prompt injection
(like this file, or a skill that teaches injection defence) can trip
MANIP-01/02. Context decides — read the surrounding lines.

## Secret access

| ID | Severity | Detects |
|---|---|---|
| SECRET-01 | critical | paths to `~/.ssh`, `id_rsa`, `id_ed25519`, `.aws/credentials`, `.gnupg` |
| SECRET-02 | high | opening/reading a `.env` file |
| SECRET-03 | high | `os.environ["...KEY / TOKEN / SECRET / PASSWORD"]` |
| SECRET-04 | high | instructing the agent to ask the user for a password / API key / token |
| SECRET-05 | medium | reading/dumping the OS keychain or credential manager |

**Legitimate cases:** a deployment skill may genuinely need one named API
key. One SECRET finding with a clear explanation in the skill's README is a
very different signal from a key read with no explanation.

## Shell execution

| ID | Severity | Detects |
|---|---|---|
| SHELL-01 | high | `subprocess.run/Popen/call`, `os.system(` |
| SHELL-02 | critical | `curl`/`wget` piped into `sh`/`bash`/`python` |
| SHELL-03 | high | `eval(` / `exec(` |
| SHELL-04 | high | `child_process.exec/spawn`, Go/Java exec equivalents |
| SHELL-05 | medium | encoded PowerShell (`-enc`) |

**Legitimate cases:** build/dev skills run commands — that's their job.
What matters: are commands fixed strings, or built from remote/user input?
Is there a `curl | sh` anywhere? (There is never a good reason for that one.)

## Network exfiltration

| ID | Severity | Detects |
|---|---|---|
| NET-01 | critical | known drop/paste endpoints (webhook.site, requestbin, pastebin, transfer.sh…) |
| NET-02 | high | hard-coded raw-IP URLs |
| NET-03 | medium | outbound POST via requests/httpx/urllib/fetch/axios |
| NET-04 | medium | raw socket connections |

**Legitimate cases:** API-wrapper skills POST to their API — check the
destination is the documented service, and look at *what* is being sent.

## Persistence

| ID | Severity | Detects |
|---|---|---|
| PERSIST-01 | high | cron, systemd, launchctl/LaunchAgents, scheduled tasks, startup folder |
| PERSIST-02 | medium | edits to `.bashrc`/`.zshrc`/`.profile`, registry Run keys |
| PERSIST-03 | medium | `chmod 777`, `sudo` |

A skill that survives reboots is a skill you can't uninstall by deleting a
folder. Almost no skill needs this. Ask hard questions.

## Obfuscation

| ID | Severity | Detects |
|---|---|---|
| OBF-01 | high | base64-looking blobs ≥ 120 chars |
| OBF-02 | medium | long hex-escaped (`\xNN`) strings |
| OBF-03 | medium | runtime base64 decoding (`b64decode`, `atob`, `base64 -d`) |

Readable code can be reviewed. Blobs can't. Any obfuscation in a skill
should come with a very good explanation.

## Broad permissions

| ID | Severity | Detects |
|---|---|---|
| PERM-01 | medium | `--no-sandbox`, disabling security/sandbox/firewall |
| PERM-02 | low | "full/unrestricted access", "any file on the system" |

---

## Proposing a new rule

Open an issue or PR with: the pattern, a real-world example (a skill in the
wild or a write-up), your proposed severity, and one innocent sentence the
rule must *not* fire on. See [CONTRIBUTING.md](../CONTRIBUTING.md).

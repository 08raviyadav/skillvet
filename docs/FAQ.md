# FAQ

### Is SkillVet an antivirus? A sandbox?
No. SkillVet is a **static, pattern-based linter for agent instructions
and bundled scripts**. It reads text and flags known-dangerous patterns.
It never executes the skill, and it cannot catch a cleverly hidden payload.
Think of it as the smoke alarm, not the fire brigade.

### A popular skill scored badly. Is it malware?
Not necessarily. Scores measure **red-flag density**, not intent. A DevOps
skill legitimately runs shell commands (SHELL findings) and may read one
documented API key (a SECRET finding). Read the findings: flags the author
explains in their README are a different signal from flags nobody mentions.
What a bad score always means: *this one deserves a careful read before
you install it.*

### A skill scored 100/A. Is it guaranteed safe?
No. A 100 means "none of the 27 known patterns were found." Novel attacks,
logic-level tricks, and anything fetched at runtime are outside what a
static scan can see. SkillVet raises the floor; it doesn't lower the need
for judgement.

### Why does SkillVet flag its own documentation?
Because the docs quote dangerous commands as examples (this FAQ mentions
`curl | sh` patterns, the rule reference quotes trigger phrases).
Pattern matchers can't tell a warning from an instruction. In your own
projects, the same thing will happen with security docs and test
fixtures — treat those findings as the known-false-positive tax, and if a
rule fires on *prose* constantly, please file a false-positive issue: the
fix is a narrower pattern.

### What file types does it scan?
Markdown, text, Python, shell, JavaScript/TypeScript, JSON, YAML, TOML,
and PowerShell. Binary files and files over 2 MB are skipped, as are
`.git`, `node_modules`, and virtualenv directories.

### Does SkillVet send my files anywhere?
No. It has zero dependencies and makes zero network calls. You can verify
that in the one file it ships as — that's rather the point of the project.

### Can I allowlist a rule for my repo?
Not yet — a `skillvet.toml` allowlist is on the roadmap. Until then, the
pragmatic options are `--fail-under` tuning in CI, or scanning only the
skill folders (not your docs) in the pre-commit hook.

### How do I dispute a finding on my own skill?
Open a **False positive** issue with the rule ID, the flagged line, and why
the pattern is innocent in context. Good false-positive reports regularly
become narrower, better rules — they're some of the most valuable issues
this project gets.

### Which agents / skill formats does this cover?
Anything text-based: `SKILL.md` skills (Muse, Muse, and compatible
agents), MCP server configs, custom GPT / agent instruction files, and the
scripts bundled with them. The threat model — instructions + scripts +
requested secrets — is the same across all of them.

# Launch Kit — SkillVet

Trending is a distribution game as much as a code game. Assets below are
ready to paste. Best launch window: **Tue–Thu, ~13:00–16:00 UTC**
(HN + US dev Twitter/X awake, Europe still online).

## 1. Hacker News (Show HN) — the big one

**Title:**
`Show HN: SkillVet – scan AI agent skills for prompt injection and secret theft before installing`

**Body:**
> Agent skills and MCP configs are the new npm packages: thousands of them,
> one-click installs, written by strangers — except a skill can instruct
> your agent, ship shell scripts, and ask for your API keys.
>
> I built SkillVet after realizing I was installing skills I hadn't read.
> It's a single zero-dependency Python file that statically scans a skill
> (SKILL.md + bundled scripts + MCP configs) for 27 red-flag patterns in 7
> categories: instruction manipulation ("ignore previous instructions",
> "don't tell the user"), secret access (~/.ssh, .env, env API keys),
> shell execution (curl | sh, eval), exfil endpoints, persistence,
> obfuscation, and over-broad permissions. It prints a 0–100 score with
> line-by-line findings, has a JSON mode + exit codes for CI, and ships as
> a GitHub Action.
>
> The repo includes a deliberately evil sample skill (scores 0/F) and a
> clean one (100/A) so you can see exactly what it catches. It's pattern
> matching, not magic — limitations are stated plainly in the README.
> Rule PRs very welcome; false positives count as bugs.

First comment (post immediately): link the two example reports + invite
people to paste scores of popular skills in the thread.

## 2. Reddit

- **r/ClaudeAI, r/ChatGPTCoding, r/LocalLLaMA** — title:
  `I scanned agent skills before installing them and found the ecosystem has a "curl | sh" problem — so I open-sourced the scanner`
  Lead with the evil-skill findings screenshot/output, tool second.
- **r/programming / r/netsec** — security angle, limitations up front.

## 3. X / Twitter thread

1. `You're installing AI agent skills written by strangers. They can run shell commands and read your API keys. I built the 10-second check that should happen first 🧵`
2. Screenshot: evil skill scoring 0/F with the `~/.ssh/id_rsa` finding.
3. `27 rules, 7 categories: prompt injection, secret access, shell exec, exfil, persistence, obfuscation, over-broad perms.`
4. `One file. Zero dependencies. Also a GitHub Action so your repo can reject risky skills in CI.`
5. `It's pattern matching, not a sandbox — limitations are in the README, stated plainly. Rule PRs welcome.` + repo link.

## 4. Dev.to / Hashnode article

Title: *"Your AI agent's skills can read your SSH keys. Here's how to check them first."*
Reuse the HN body + a section walking through each category with the
bundled evil example.

## 5. Seeding checklist

- [ ] Repo topics: `ai-agents`, `security`, `prompt-injection`, `mcp`,
      `claude`, `llm`, `scanner`, `devtools`
- [ ] Pin the repo on the GitHub profile
- [ ] Post in 2–3 Discord/Slack communities (agent/MCP focused), in
      showcase channels only, with the demo output
- [ ] Reply to every issue/comment in the first 48h — velocity matters
- [ ] If it lands on HN front page, do NOT post anywhere else that day;
      ride the thread.

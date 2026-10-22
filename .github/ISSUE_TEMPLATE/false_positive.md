---
name: False positive report
about: SkillVet flagged something innocent — help us narrow the rule
title: "[False positive] RULE-ID: "
labels: false-positive
---

**Rule ID**
e.g. MANIP-01

**The flagged line**
```
Paste the exact line SkillVet flagged.
```

**Where it appears**
Skill name + file, and what the surrounding text is doing (docs? tests?
a security tutorial? a legit deployment step?).

**Why it's innocent here**
What the line actually does in context.

**Suggested narrower pattern (optional)**
If you have an idea for a pattern that still catches the real thing,
share it — these suggestions often become the fix.

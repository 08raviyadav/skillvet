# Contributing to SkillVet

The highest-value contribution is a **new detection rule** — or a real-world
skill (good or bad) that SkillVet currently scores wrong.

## Adding a rule

1. Add the pattern to `RAW_RULES` in `skillvet.py` with:
   - a stable ID (`CATEGORY-NN`),
   - a severity (`critical` / `high` / `medium` / `low`) — be honest,
     grade inflation makes scores meaningless,
   - a one-line "why it matters" a non-security person understands.
2. Add a matching fixture line to `examples/` or a test case in
   `tests/test_skillvet.py` proving the rule fires — and a clean example
   proving it doesn't fire on innocent text.
3. Run the tests: `python3 tests/test_skillvet.py`

## Ground rules

- **Zero dependencies, forever.** The scanner stays one stdlib-only file.
- No rule without a plausible real-world example behind it.
- False positives are bugs too — if a rule fires on normal documentation
  (like this README discussing `curl | sh` as a threat), the rule needs a
  narrower pattern, not a shrug.

## Pull requests

Branch from `main`, keep PRs single-purpose, and include the before/after
scores on the bundled examples when you touch the engine.

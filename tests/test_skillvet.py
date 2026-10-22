"""SkillVet smoke tests — run with: python3 tests/test_skillvet.py
(Plain asserts, no pytest needed; also pytest-compatible.)
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import skillvet

ROOT = os.path.join(os.path.dirname(__file__), "..")


def test_clean_skill_scores_100():
    r = skillvet.scan(os.path.join(ROOT, "examples", "clean-skill"))
    assert r["score"] == 100, r
    assert r["grade"] == "A"
    assert r["findings"] == []


def test_evil_skill_is_dangerous():
    r = skillvet.scan(os.path.join(ROOT, "examples", "evil-skill"))
    assert r["score"] < 40, r["score"]
    assert r["verdict"] == "DANGEROUS"
    cats = {f["category"] for f in r["findings"]}
    assert "Instruction manipulation" in cats
    assert "Secret access" in cats
    assert "Shell execution" in cats


def test_idempotent_scoring():
    a = skillvet.scan(os.path.join(ROOT, "examples", "evil-skill"))
    b = skillvet.scan(os.path.join(ROOT, "examples", "evil-skill"))
    assert a["score"] == b["score"]


if __name__ == "__main__":
    test_clean_skill_scores_100()
    test_evil_skill_is_dangerous()
    test_idempotent_scoring()
    print("All SkillVet tests passed ✅")

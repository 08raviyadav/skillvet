# Changelog

All notable changes to this project are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Planned
- `skillvet.toml` per-repo allowlist configuration
- SARIF output for GitHub code scanning
- MCP tool-poisoning deep-checks

## [0.1.0] - 2026-10-22

### Added
- Single-file, zero-dependency scanner (`skillvet.py`) for agent skills,
  MCP configs, and instruction files
- 27 detection rules across 7 categories: instruction manipulation,
  secret access, shell execution, network exfiltration, persistence,
  obfuscation, broad permissions
- 0–100 scoring with A–F grades and plain-language findings
  (file, line, excerpt, explanation)
- JSON report output and CI-friendly exit codes (`--fail-under`)
- `--list-rules` and `--version` CLI flags
- GitHub Action (`action.yml`) with report artifact upload
- Bundled examples: a clean skill (100/A) and a deliberately malicious
  skill (0/F)
- Documentation: usage guide, full rule reference, FAQ

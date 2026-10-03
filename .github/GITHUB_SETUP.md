# GitHub setup checklist for the repo

This file captures the remaining GitHub configuration actions that can’t be enforced from the repository itself but are recommended for a mature private deployment.

## 1) Protect the `main` branch

In GitHub: Settings → Branches → Add branch protection rule for `main`.

Recommended settings:

- Require a pull request before merging
- Require 1 approving review
- Dismiss stale PR approvals when new commits are pushed
- Require conversation resolution before merge
- Require status checks to pass before merging
- Required checks:
  - `Semgrep security scan`
  - `Test (Python 3.11)`
  - `Test (Python 3.12)`
- Restrict who can push to `main`

## 2) Use GitHub Issues as the incident/bug queue

The repository already has GitHub Issues enabled. To keep the queue clean:

- Use the bug report template in `.github/ISSUE_TEMPLATE/bug_report.yml`
- Label issues consistently (`bug`, `security`, `enhancement`, `docs`, `ops`, `question`)
- Route security reports through `.github/SECURITY.md` rather than a public issue

## 3) Decide on project tracking and collaboration channels

The repository metadata already indicates project support is available, but the operating model should be explicit:

- Use GitHub Projects for roadmap and execution tracking if you want a visible backlog
- Keep GitHub Discussions enabled for non-sensitive architectural conversations
- Keep the wiki disabled unless you want a separate knowledge base

A reasonable setup for a private repo is:

- GitHub Projects: enabled for roadmap tracking
- GitHub Discussions: enabled for architecture/feedback
- Wiki: disabled unless a team-specific internal knowledge base is required

## 4) Keep security review plugged into CI

The repo already contains a CI workflow in `.github/workflows/ci.yml` with:

- Semgrep security scan
- Python linting
- PyCompile verification
- Unit tests across Python 3.11 and 3.12

These checks should be required in the branch protection rule above.

## 5) Define an operational release cadence

Recommended process:

1. Create a feature branch for each change
2. Open a PR against `main`
3. Run required checks and review the diff
4. Merge with squash strategy
5. Tag release versions if the model or pipeline contract changes materially

## 6) Optional: add repository automation

If you want to tighten GitHub hygiene further, add:

- a CODEOWNERS file for ownership and review routing
- issue labels for `priority`, `risk`, and `agentic-ai`
- release notes or changelog automation

This repo is already close to a good GitHub operational baseline; the remaining work is mostly configuration in the GitHub UI rather than code.

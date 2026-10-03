# GitHub setup — current state and limits

The repo is **private** on the **GitHub Free** plan. Settings that can't be enforced from the repository itself:

| Setting | Status |
|---------|--------|
| Branch protection on `main` | **Unavailable** — needs GitHub Pro/Team for private repos. Convention instead: every change goes through a PR and CI (`Semgrep security scan`, `Test (Python 3.11)`, `Test (Python 3.12)`) must be green before merging. |
| Secret scanning | **Unavailable** on private repos without Advanced Security. `SecretGuard` and the pre-commit private-key hook are the substitutes. |
| Dependabot version updates | **On**, via `.github/dependabot.yml`. |
| Dependabot alerts / security updates | Enable in Settings → Code security (free for private repos). |
| Repo secrets | None required — CI makes no API calls. |

## Conventions

- Security reports: root [`SECURITY.md`](../SECURITY.md) (email, not public issues).
- Issues: forms in `.github/ISSUE_TEMPLATE/` (`bug_report.yml`, `feature_request.md`).
- Reviews: `.github/CODEOWNERS`.
- Merges: PR → green CI → merge. Keep `CHANGELOG.md`, test counts and version banners in sync; `scripts/check_docs_sync.py` enforces this in CI and pre-commit.
- Operational procedures: [`docs/runbooks/`](../docs/runbooks/).

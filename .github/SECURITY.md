# Security Policy

## Supported Versions

The project is currently maintained on the `main` branch and is evaluated for security issues against the latest release in active development.

| Version | Supported |
| --- | --- |
| `main` | ✅ Yes |
| other branches | ⚠️ Best effort, please report a vulnerability regardless of branch |

## Reporting a Vulnerability

Please do not open a public GitHub issue for security vulnerabilities.

Instead, report privately to the maintainer at:

- `vinoth.n@outlook.com`
- Or use the repository owner’s private reporting channel if one is configured

Please include:

- Summary of the issue
- Affected files or modules
- Reproduction steps
- Impact assessment
- Suggested remediation

## Response Timeline

We aim to acknowledge reports within 3 business days and provide a remediation estimate as quickly as possible based on impact and complexity.

## Defensive Expectations

This repository contains AI pipeline code, LLM integrations, and a private dataset pipeline. Please avoid creating issues for:

- leaked API keys or credentials
- secrets present in logs or outputs
- exploitation paths that expose private infrastructure or model access

Please use responsible disclosure and avoid sharing private tokens or confidential data in public discussions.

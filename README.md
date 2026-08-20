![Lifecycle:Maturing](https://img.shields.io/badge/Lifecycle-Maturing-007EC6)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=bcgov_ppr&metric=alert_status)](https://sonarcloud.io/dashboard?id=bcgov_ppr)[![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=bcgov_ppr&metric=ncloc)](https://sonarcloud.io/dashboard?id=bcgov_ppr)

# ppr
Personal Property Registry

## Development

This repo hosts `ppr-ui`, `ppr-api` and `mhr-api` as independent services - see each subfolder's own README for local setup.

Pre-commit hooks (lint per-service, plus [gitleaks](https://github.com/gitleaks/gitleaks) secret scanning across the whole repo) are managed at the repo root with [Lefthook](https://github.com/evilmartians/lefthook). Run `pnpm install` once at the repo root to set them up - no per-service setup needed. If a commit is blocked by a false-positive secret match, add an allowlist entry to `.gitleaks.toml` rather than committing with `--no-verify`.

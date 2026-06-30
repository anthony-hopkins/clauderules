# CI/CD

**Applies when:** editing CI/CD pipelines (GitHub Actions, GitLab CI, Jenkins, Azure Pipelines).

Source: GENERAL_CLAUDE.md § CI/CD.

Discover CI from .github/workflows/, .gitlab-ci.yml, Jenkinsfile, etc. Follow existing patterns.

## CI jobs (reference)

- **lint-typecheck:** frozen lockfile install, lint, typecheck
- **test:** service containers if needed, migrations in test context, coverage
- **security-scan:** dependency audit + filesystem/container scan (Trivy, etc.)

## Deploy workflow (reference)

Build artifacts → migrations in deploy context → deploy via discovered mechanism → smoke test.

## Rules

- Pinned runtime versions matching production
- Secrets via CI secret store — never in workflow files
- Failed security scan at configured severity blocks merge

# Changelog

All notable changes to this project are documented in this file.

## 0.1.4 - 2026-10-06
- Install Boto3 with CRT support automatically for AWS login credentials.
- Require Boto3 1.41+ for the AWS login credential provider.
- Report failed scans as incomplete instead of claiming no opportunities were found.
- Stop bulk apply on incomplete scans and keep the interactive menu usable after errors.
- Document pipx, virtual environment installation, and the Homebrew tap distribution path.

## 0.1.3 - 2026-02-28
- Added safer bulk apply workflow: `apply --all --service <scope>` with confirmation and dry-run support.
- Improved apply command UX with explicit `--service` for single-resource operations and clearer usage errors.
- Added interactive `menu` command (WonderDash-style hub) for guided analyze/apply/report flows.
- Default command now opens the interactive menu in TTY contexts (falls back to help in non-interactive shells).
- Updated README quick-start examples to document bulk apply and menu usage.

## 0.1.0 - 2026-02-11
- Initial PyPI release of `aws-cost-optimizer`.
- Added analyzers for DynamoDB, Lambda, S3, and CloudFront optimization opportunities.
- Added recommendation and apply CLI workflows.

# AWS Cost Optimizer

[![CI](https://github.com/mjfxjas/aws-cost-optimizer/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/mjfxjas/aws-cost-optimizer/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/aws-cost-optimizer.svg)](https://pypi.org/project/aws-cost-optimizer/)

CLI for inspecting DynamoDB, Lambda, S3, and CloudFront configuration and applying selected changes.

## Features

- **DynamoDB Analysis**: List tables using on-demand capacity
- **Lambda Analysis**: Find functions without reserved concurrency limits
- **S3 Analysis**: Detect buckets missing lifecycle policies
- **CloudFront Analysis**: Flag distributions with low default cache TTLs
- **Terminal output**: Tables of findings and suggested actions

## Installation

```bash
pip install aws-cost-optimizer
```

## Quick Start

```bash
# Analyze all services
aws-cost-optimizer analyze

# Analyze specific service
aws-cost-optimizer analyze --service dynamodb

# Preview bulk changes
aws-cost-optimizer apply --all --service all --dry-run

# Live execute (requires explicit --execute)
aws-cost-optimizer apply --all --service all --execute

# Single-resource workflow
aws-cost-optimizer apply --service dynamodb my-table --dry-run
aws-cost-optimizer apply --service dynamodb my-table --execute

# Interactive menu
aws-cost-optimizer menu
```

## Smoke Test
Verify the installed package and CLI:

```bash
python3 -m pip install --upgrade aws-cost-optimizer
aws-cost-optimizer --help
python3 -c "from importlib.metadata import version; print(version('aws-cost-optimizer'))"
```

## Security Checks
- CI runs Bandit static analysis on `src/aws_cost_optimizer` in the Python 3.12 job.
- The CI scan reports issues at medium severity or higher.

```bash
bandit -r src/aws_cost_optimizer --severity-level medium --confidence-level medium
```

## Requirements

- Python 3.9+
- AWS credentials configured
- IAM permissions for read access to analyzed services

## Development

```bash
git clone https://github.com/mjfxjas/aws-cost-optimizer
cd aws-cost-optimizer
pip install -e .
```

## License

MIT. See `LICENSE`.

## Changelog

See `CHANGELOG.md` for versioned release notes.

## Author

Jonathan Schimpf - [jon@theatrico.org](mailto:jon@theatrico.org)

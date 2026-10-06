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

For a CLI installation on macOS, use pipx. It manages an isolated Python
environment and puts the command on your PATH:

```bash
brew install pipx
pipx ensurepath
# Open a new terminal after ensurepath, then:
pipx install aws-cost-optimizer
aws-cost-optimizer --help
```

Upgrade an existing pipx installation with `pipx upgrade aws-cost-optimizer`.

Alternatively, install into a virtual environment (Python 3.9+):

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install aws-cost-optimizer
```

Version 0.1.4 and later install Boto3 with AWS Common Runtime (CRT) support
for credentials created by `aws login`. AWS credentials and a default region
must still be configured. Named profiles can be selected with `AWS_PROFILE`.

For an older installation showing the missing `botocore[crt]` dependency error,
run `python -m pip install 'botocore[crt]'` inside its active virtual environment.

### Homebrew distribution

Install from the shared [Homebrew tap](https://github.com/mjfxjas/homebrew-tap):

```bash
brew install mjfxjas/tap/aws-cost-optimizer
aws-cost-optimizer --help
```

Homebrew manages Python and all dependencies, including AWS CRT. No virtual
environment activation is needed. See [the Homebrew guide](docs/homebrew.md)
for release updates and adding other programs to the shared tap.

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
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m unittest discover -s tests -v
```

## License

MIT. See `LICENSE`.

## Changelog

See `CHANGELOG.md` for versioned release notes.

## Author

Jonathan Schimpf - [jon@theatrico.org](mailto:jon@theatrico.org)

# AWS Cost Optimizer

[![CI](https://github.com/mjfxjas/aws-cost-optimizer/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/mjfxjas/aws-cost-optimizer/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/aws-cost-optimizer.svg)](https://pypi.org/project/aws-cost-optimizer/)

Automated AWS cost optimization recommendations based on production experience achieving 60% cost reduction.

## Features

- **DynamoDB Analysis**: Identify tables that should use provisioned capacity
- **Lambda Analysis**: Find functions without reserved concurrency limits
- **S3 Analysis**: Detect buckets missing lifecycle policies
- **CloudFront Analysis**: Identify distributions with suboptimal cache settings
- **Rich CLI**: Beautiful terminal output with actionable recommendations

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

PyPI publication does not create a Homebrew formula. A dedicated Homebrew tap
can provide `brew install mjfxjas/tap/aws-cost-optimizer` once a
`mjfxjas/homebrew-tap` repository and its formula have been published. This tap
is not set up by this repository. Until then, use the pipx commands above.
See [the Homebrew guide](docs/homebrew.md) for release, tap creation, dependency
generation, testing, and publishing steps for this and your other programs.

The formula should install a released source archive into its own virtual
environment using `Language::Python::Virtualenv`, declare Python and all
transitive dependencies (including `awscrt`) with checksummed resources, and
verify `aws-cost-optimizer --help` without needing AWS credentials.

## Quick Start

```bash
# Analyze all services
aws-cost-optimizer analyze

# Analyze specific service
aws-cost-optimizer analyze --service dynamodb

# Bulk apply workflow (safe-first)
aws-cost-optimizer apply --all --service all --dry-run

# Live execute (requires explicit --execute)
aws-cost-optimizer apply --all --service all --execute

# Single-resource workflow
aws-cost-optimizer apply --service dynamodb my-table --dry-run
aws-cost-optimizer apply --service dynamodb my-table --execute

# Interactive menu/hub (includes "Apply all (EXECUTE)")
aws-cost-optimizer menu
```

## Common Operator Flows
A few high-signal commands to show what the tool is for:

```bash
# Full analysis pass across supported services
aws-cost-optimizer analyze

# Guided terminal experience
aws-cost-optimizer menu

# Safe bulk apply preview
aws-cost-optimizer apply --all --service all --dry-run
```

## Smoke Test
Quick verification that install and CLI wiring are healthy:

```bash
python3 -m pip install --upgrade aws-cost-optimizer
aws-cost-optimizer --help
python3 -c "from importlib.metadata import version; print(version('aws-cost-optimizer'))"
```

## Security Checks
- CI runs Bandit static security analysis on `src/aws_cost_optimizer` (Python 3.11 job).
- Failing threshold is set to medium-or-higher severity/confidence.

```bash
bandit -r src/aws_cost_optimizer --severity-level medium --confidence-level medium
```

## Example Output

```
Service: DynamoDB | Resource: my-table | Issue: Using on-demand | Savings: ~40-60% | Action: Switch to provisioned
Service: Lambda | Resource: my-function | Issue: No concurrency limit | Savings: Prevent overruns | Action: Set reserved concurrency
Service: S3 | Resource: my-bucket | Issue: No lifecycle policy | Savings: ~20-30% | Action: Add lifecycle rules
```

## Real-World Results

This tool is based on optimizations that achieved:
- **60% cost reduction** on production serverless application
- **90% reduction** in Lambda invocations via CloudFront caching
- **Predictable costs** through provisioned capacity

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

AWS Solutions Architect Associate with production experience optimizing cloud costs.

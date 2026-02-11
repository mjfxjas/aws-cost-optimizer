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

```bash
pip install aws-cost-optimizer
```

## Quick Start

```bash
# Analyze all services
aws-cost-optimizer analyze

# Analyze specific service
aws-cost-optimizer analyze --service dynamodb

# Apply optimization (dry-run first)
aws-cost-optimizer apply dynamodb my-table --dry-run
aws-cost-optimizer apply dynamodb my-table
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
pip install -e .
```

## License

MIT. See `LICENSE`.

## Changelog

See `CHANGELOG.md` for versioned release notes.

## Author

Jonathan Schimpf - [jon@theatrico.org](mailto:jon@theatrico.org)

AWS Solutions Architect Associate with production experience optimizing cloud costs.

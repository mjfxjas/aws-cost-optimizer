# AWS Cost Optimizer

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

## Example Output

```
Cost Optimization Recommendations
┏━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Service   ┃ Resource    ┃ Issue                  ┃ Savings  ┃ Action                    ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ DynamoDB  │ my-table    │ Using on-demand        │ ~40-60%  │ Switch to provisioned     │
│ Lambda    │ my-function │ No concurrency limit   │ Prevent  │ Set reserved concurrency  │
│ S3        │ my-bucket   │ No lifecycle policy    │ ~20-30%  │ Add lifecycle rules       │
└───────────┴─────────────┴────────────────────────┴──────────┴───────────────────────────┘
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

MIT License - Jonathan Schimpf

## Author

Jonathan Schimpf - [jon@theatrico.org](mailto:jon@theatrico.org)

AWS Solutions Architect Associate with production experience optimizing cloud costs.

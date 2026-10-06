"""Cost optimization analyzers for AWS services"""
from typing import List, Dict

import boto3
from botocore.exceptions import ClientError


class AnalysisError(RuntimeError):
    """An analyzer could not complete; its findings must not imply success."""

def analyze_dynamodb() -> List[Dict]:
    """Analyze DynamoDB tables for cost optimization"""
    recommendations = []
    try:
        dynamodb = boto3.client('dynamodb')
        tables = dynamodb.list_tables()['TableNames']
        
        for table_name in tables:
            table = dynamodb.describe_table(TableName=table_name)['Table']
            billing_mode = table.get('BillingModeSummary', {}).get('BillingMode', 'PROVISIONED')
            
            if billing_mode == 'PAY_PER_REQUEST':
                # Check if provisioned would be cheaper
                recommendations.append({
                    'service': 'DynamoDB',
                    'resource': table_name,
                    'issue': 'Using on-demand pricing',
                    'savings': '~40-60%',
                    'action': 'Switch to provisioned capacity'
                })
    except Exception as err:
        raise AnalysisError(f"DynamoDB analyzer failed: {err}") from err
    
    return recommendations

def analyze_lambda() -> List[Dict]:
    """Analyze Lambda functions for cost optimization"""
    recommendations = []
    try:
        lambda_client = boto3.client('lambda')
        functions = lambda_client.list_functions()['Functions']
        
        for func in functions:
            # Check for reserved concurrency
            if 'ReservedConcurrentExecutions' not in func:
                recommendations.append({
                    'service': 'Lambda',
                    'resource': func['FunctionName'],
                    'issue': 'No reserved concurrency limit',
                    'savings': 'Prevent runaway costs',
                    'action': 'Set reserved concurrency'
                })
    except Exception as err:
        raise AnalysisError(f"Lambda analyzer failed: {err}") from err
    
    return recommendations

def analyze_s3() -> List[Dict]:
    """Analyze S3 buckets for cost optimization"""
    recommendations = []
    try:
        s3 = boto3.client('s3')
        buckets = s3.list_buckets()['Buckets']
        
        for bucket in buckets:
            bucket_name = bucket['Name']
            
            # Check for lifecycle policies
            try:
                s3.get_bucket_lifecycle_configuration(Bucket=bucket_name)
            except ClientError as err:
                code = err.response.get('Error', {}).get('Code', '')
                if code == 'NoSuchLifecycleConfiguration':
                    recommendations.append({
                        'service': 'S3',
                        'resource': bucket_name,
                        'issue': 'No lifecycle policy',
                        'savings': '~20-30%',
                        'action': 'Add lifecycle rules for old objects'
                    })
                else:
                    raise AnalysisError(
                        f"S3 lifecycle check failed for {bucket_name}: {err}"
                    ) from err
    except Exception as err:
        raise AnalysisError(f"S3 analyzer failed: {err}") from err
    
    return recommendations

def analyze_cloudfront() -> List[Dict]:
    """Analyze CloudFront distributions for cost optimization"""
    recommendations = []
    try:
        cloudfront = boto3.client('cloudfront')
        distributions = cloudfront.list_distributions().get('DistributionList', {}).get('Items', [])
        
        for dist in distributions:
            # Check cache settings
            default_ttl = dist['DefaultCacheBehavior'].get('DefaultTTL', 0)
            if default_ttl < 3600:
                recommendations.append({
                    'service': 'CloudFront',
                    'resource': dist['Id'],
                    'issue': f'Low cache TTL ({default_ttl}s)',
                    'savings': '~50-90% origin requests',
                    'action': 'Increase cache TTL to 3600s+'
                })
    except Exception as err:
        raise AnalysisError(f"CloudFront analyzer failed: {err}") from err
    
    return recommendations

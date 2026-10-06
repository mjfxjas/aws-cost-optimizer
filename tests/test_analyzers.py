"""Contract tests using stubbed AWS APIs; no credentials or network required."""
from unittest.mock import patch

import boto3
import pytest
from botocore.stub import Stubber

from aws_cost_optimizer import analyzers


def client(service):
    return boto3.client(service, region_name='us-east-1',
                        aws_access_key_id='testing', aws_secret_access_key='testing')


@pytest.mark.parametrize('limit', [0, 10])
def test_explicit_lambda_concurrency_is_not_flagged(limit):
    aws = client('lambda')
    with Stubber(aws) as stub, patch.object(analyzers.boto3, 'client', return_value=aws):
        stub.add_response('list_functions', {'Functions': [{'FunctionName': 'configured'}]}, {})
        stub.add_response('get_function_concurrency', {'ReservedConcurrentExecutions': limit},
                          {'FunctionName': 'configured'})
        assert analyzers.analyze_lambda() == []
        stub.assert_no_pending_responses()


def test_lambda_pagination_and_missing_concurrency():
    aws = client('lambda')
    with Stubber(aws) as stub, patch.object(analyzers.boto3, 'client', return_value=aws):
        stub.add_response('list_functions', {'Functions': [{'FunctionName': 'first'}], 'NextMarker': 'next'}, {})
        stub.add_response('get_function_concurrency', {'ReservedConcurrentExecutions': 10}, {'FunctionName': 'first'})
        stub.add_response('list_functions', {'Functions': [{'FunctionName': 'second'}]}, {'Marker': 'next'})
        stub.add_response('get_function_concurrency', {}, {'FunctionName': 'second'})
        assert [r['resource'] for r in analyzers.analyze_lambda()] == ['second']
        stub.assert_no_pending_responses()


def test_lambda_access_denied_does_not_hide_other_functions(caplog):
    aws = client('lambda')
    with Stubber(aws) as stub, patch.object(analyzers.boto3, 'client', return_value=aws):
        stub.add_response('list_functions', {'Functions': [{'FunctionName': 'denied'}, {'FunctionName': 'allowed'}]}, {})
        stub.add_client_error('get_function_concurrency', service_error_code='AccessDeniedException',
                              expected_params={'FunctionName': 'denied'})
        stub.add_response('get_function_concurrency', {}, {'FunctionName': 'allowed'})
        assert [r['resource'] for r in analyzers.analyze_lambda()] == ['allowed']
        assert 'denied' in caplog.text
        stub.assert_no_pending_responses()


def test_dynamodb_pagination():
    aws = client('dynamodb')
    with Stubber(aws) as stub, patch.object(analyzers.boto3, 'client', return_value=aws):
        stub.add_response('list_tables', {'TableNames': ['first'], 'LastEvaluatedTableName': 'first'}, {})
        stub.add_response('describe_table', {'Table': {'TableName': 'first', 'BillingModeSummary': {'BillingMode': 'PROVISIONED'}}}, {'TableName': 'first'})
        stub.add_response('list_tables', {'TableNames': ['second']}, {'ExclusiveStartTableName': 'first'})
        stub.add_response('describe_table', {'Table': {'TableName': 'second', 'BillingModeSummary': {'BillingMode': 'PAY_PER_REQUEST'}}}, {'TableName': 'second'})
        assert [r['resource'] for r in analyzers.analyze_dynamodb()] == ['second']
        stub.assert_no_pending_responses()

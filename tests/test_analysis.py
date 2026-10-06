import unittest
from contextlib import ExitStack
from unittest.mock import Mock, patch

from botocore.exceptions import ClientError, MissingDependencyException
from click.testing import CliRunner

from aws_cost_optimizer import analyzers
from aws_cost_optimizer.cli import console, main, menu


class AnalysisTests(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def test_missing_dependency_is_not_a_clean_scan(self):
        error = MissingDependencyException(msg='Install botocore[crt]')
        with patch.object(analyzers.boto3, 'client', side_effect=error):
            result = self.runner.invoke(main, ['analyze'])
        self.assertEqual(result.exit_code, 1)
        self.assertIn('Analysis incomplete', result.output)
        for service in ('DynamoDB', 'Lambda', 'S3', 'CloudFront'):
            self.assertIn(f'{service} analyzer failed', result.output)
        self.assertNotIn('No cost optimization opportunities', result.output)

    def test_clean_scan_reports_no_findings(self):
        with ExitStack() as stack:
            for service in ('dynamodb', 'lambda', 's3', 'cloudfront'):
                stack.enter_context(patch.object(analyzers, f'analyze_{service}', return_value=[]))
            result = self.runner.invoke(main, ['analyze'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('No cost optimization opportunities', result.output)

    def test_partial_scan_blocks_bulk_apply(self):
        finding = {'service': 'DynamoDB', 'resource': 'example-table'}
        with ExitStack() as stack:
            stack.enter_context(patch.object(analyzers, 'analyze_dynamodb', return_value=[finding]))
            stack.enter_context(patch.object(analyzers, 'analyze_lambda', side_effect=analyzers.AnalysisError('Lambda failed')))
            for service in ('s3', 'cloudfront'):
                stack.enter_context(patch.object(analyzers, f'analyze_{service}', return_value=[]))
            apply = stack.enter_context(patch('aws_cost_optimizer.cli._execute_recommendation'))
            result = self.runner.invoke(main, ['apply', '--all', '--execute', '--yes'])
        self.assertEqual(result.exit_code, 1)
        self.assertIn('Analysis incomplete', result.output)
        self.assertNotIn('Nothing to apply', result.output)
        apply.assert_not_called()

    def test_single_service_does_not_call_other_analyzers(self):
        with patch.object(analyzers, 'analyze_dynamodb', return_value=[]), patch.object(analyzers, 'analyze_lambda') as other:
            result = self.runner.invoke(main, ['analyze', '--service', 'dynamodb'])
        self.assertEqual(result.exit_code, 0)
        other.assert_not_called()

    def test_menu_recovers_from_analysis_failure(self):
        with patch('aws_cost_optimizer.cli.sys.stdin.isatty', return_value=True), patch('aws_cost_optimizer.cli.IntPrompt.ask', side_effect=[1, 0]), patch.object(analyzers.boto3, 'client', side_effect=RuntimeError('Credentials expired')):
            with console.capture() as capture:
                menu.callback()
        output = capture.get()
        self.assertIn('Analysis incomplete', output)
        self.assertIn('Bye.', output)
        self.assertNotIn('No cost optimization opportunities', output)

    def test_s3_missing_policy_is_a_finding_but_denied_is_failure(self):
        client = Mock()
        client.list_buckets.return_value = {'Buckets': [{'Name': 'example-bucket'}]}
        with patch.object(analyzers.boto3, 'client', return_value=client):
            client.get_bucket_lifecycle_configuration.side_effect = ClientError(
                {'Error': {'Code': 'NoSuchLifecycleConfiguration'}}, 'GetBucketLifecycleConfiguration'
            )
            self.assertEqual(len(analyzers.analyze_s3()), 1)
            client.get_bucket_lifecycle_configuration.side_effect = ClientError(
                {'Error': {'Code': 'AccessDenied'}}, 'GetBucketLifecycleConfiguration'
            )
            with self.assertRaises(analyzers.AnalysisError):
                analyzers.analyze_s3()


if __name__ == '__main__':
    unittest.main()

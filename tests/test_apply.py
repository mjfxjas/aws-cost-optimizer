import unittest
from unittest.mock import Mock, patch

from botocore.exceptions import ClientError
from click.testing import CliRunner

from aws_cost_optimizer.cli import _apply_s3, main


class ApplyTests(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def test_single_failed_update_exits_nonzero(self):
        with patch("aws_cost_optimizer.cli._execute_recommendation", return_value=(False, "AccessDenied")):
            result = self.runner.invoke(main, ["apply", "--service", "lambda", "example", "--execute"])
        self.assertEqual(result.exit_code, 1)
        self.assertIn("Resource update failed", result.output)

    def test_bulk_attempts_remaining_resources_and_exits_nonzero(self):
        recs = [{"service": "Lambda", "resource": name} for name in ["first", "second"]]
        with patch("aws_cost_optimizer.cli._collect_recommendations", return_value=recs), patch(
            "aws_cost_optimizer.cli._execute_recommendation", side_effect=[(False, "AccessDenied"), (True, "Updated")]
        ) as execute:
            result = self.runner.invoke(main, ["apply", "--all", "--execute", "--yes"])
        self.assertEqual(result.exit_code, 1)
        self.assertEqual(execute.call_count, 2)
        self.assertIn("Success: 1/2", result.output)

    def test_successful_update_exits_zero(self):
        with patch("aws_cost_optimizer.cli._execute_recommendation", return_value=(True, "Updated")):
            result = self.runner.invoke(main, ["apply", "--service", "lambda", "example", "--execute"])
        self.assertEqual(result.exit_code, 0)

    def test_plan_and_dry_run_make_no_aws_calls(self):
        for flags in [[], ["--dry-run"], ["--execute", "--dry-run"]]:
            with self.subTest(flags=flags), patch("aws_cost_optimizer.cli.boto3.client") as client:
                result = self.runner.invoke(main, ["apply", "--service", "s3", "example", *flags])
            self.assertEqual(result.exit_code, 0)
            client.assert_not_called()

    def test_existing_lifecycle_rules_are_never_replaced(self):
        client = Mock()
        client.get_bucket_lifecycle_configuration.return_value = {
            "Rules": [{"ID": "retain-important-records", "Status": "Enabled"}]
        }
        with patch("aws_cost_optimizer.cli.boto3.client", return_value=client):
            ok, message = _apply_s3("example", {"s3_expire_days": 365})
        self.assertFalse(ok)
        self.assertIn("left unchanged", message)
        client.put_bucket_lifecycle_configuration.assert_not_called()

    def test_missing_lifecycle_policy_can_be_created(self):
        client = Mock()
        client.get_bucket_lifecycle_configuration.side_effect = ClientError(
            {"Error": {"Code": "NoSuchLifecycleConfiguration"}}, "GetBucketLifecycleConfiguration"
        )
        with patch("aws_cost_optimizer.cli.boto3.client", return_value=client):
            ok, _ = _apply_s3("example", {"s3_expire_days": 365})
        self.assertTrue(ok)
        client.put_bucket_lifecycle_configuration.assert_called_once()
        rules = client.put_bucket_lifecycle_configuration.call_args.kwargs["LifecycleConfiguration"]["Rules"]
        self.assertEqual(rules[0]["Expiration"]["Days"], 365)

    def test_denied_lifecycle_read_blocks_write(self):
        client = Mock()
        client.get_bucket_lifecycle_configuration.side_effect = ClientError(
            {"Error": {"Code": "AccessDenied"}}, "GetBucketLifecycleConfiguration"
        )
        with patch("aws_cost_optimizer.cli.boto3.client", return_value=client):
            with self.assertRaises(ClientError):
                _apply_s3("example", {"s3_expire_days": 365})
        client.put_bucket_lifecycle_configuration.assert_not_called()


if __name__ == "__main__":
    unittest.main()

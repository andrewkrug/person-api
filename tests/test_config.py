import boto3
import logging
import unittest
from moto import mock_ssm
from person_api import config
from unittest.mock import patch

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s:%(levelname)s:%(name)s:%(message)s'
)

@mock_ssm
class ConfigTest(unittest.TestCase):
    def test_get_config(self):
        everett_manager = config.get_config()
        assert everett_manager is not None

    def test_ssm_get_param(self):
        client = boto3.client('ssm', region_name='us-west-2')

        client.put_parameter(
            Name='/the/secret',
            Description='A secure test parameter',
            Value='imbatman',
            Type='SecureString',
            KeyId='alias/aws/ssm'
        )

        res = config.get_encrypted_parameter(
            parameter_name='/the/secret',
            client=client
        )

        assert res == 'imbatman'

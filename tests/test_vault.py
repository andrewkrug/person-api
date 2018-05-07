import boto3
import faker
import logging
import os
import unittest

logging.basicConfig(
   level=logging.DEBUG,
   format='%(asctime)s:%(levelname)s:%(name)s:%(message)s'
)

logging.getLogger('boto').setLevel(logging.CRITICAL)
logging.getLogger('boto3').setLevel(logging.CRITICAL)
logging.getLogger('botocore').setLevel(logging.CRITICAL)

logger = logging.getLogger(__name__)
from tests.fake_cis_v1 import FakeVault
from person_api import config
from person_api import vault


class VaultTest(unittest.TestCase):
    def setUp(self):
        fake = faker.Faker()
        self.table_name = fake.isbn10(separator="-")
        v = FakeVault(self.table_name)
        try:
            v.delete()
        except Exception as e:
            logger.error('Vault does not exist yet due to : {}'.format(e))

        if not v.is_ready():
            v.find_or_create()

            while v.is_ready() is not True:
                pass

            v.populate()

        table_name = self.table_name
        fake_dynamo = boto3.resource('dynamodb', endpoint_url='http://localhost:4567')
        fake_table = fake_dynamo.Table(table_name)
        cis_table = vault.IdentityVault(table_name)
        cis_table.table = fake_table
        os.environ["CIS_DYNAMODB_PERSON_TABLE"] = self.table_name


    def test_vault_populated(self):
        table_name = self.table_name
        fake_dynamo = boto3.resource('dynamodb', endpoint_url='http://localhost:4567')
        fake_table = fake_dynamo.Table(table_name)
        p = vault.IdentityVault(table_name)
        p.table = fake_table
        res = p.all
        assert res is not None

    def tearDown(self):
        v = FakeVault(self.table_name)
        v.delete()

        while v.is_ready is True:
            pass

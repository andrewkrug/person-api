import boto3
import faker
import logging
import os
import random
import unittest

from person_api.vault1 import DataClassification
from person_api.vault1 import IdentityVault
from tests.fake_cis_v1 import FakeVault


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s:%(levelname)s:%(name)s:%(message)s'
)

logging.getLogger('boto').setLevel(logging.CRITICAL)
logging.getLogger('boto3').setLevel(logging.CRITICAL)
logging.getLogger('botocore').setLevel(logging.CRITICAL)

logger = logging.getLogger(__name__)


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
        cis_table = IdentityVault(table_name)
        cis_table.table = fake_table
        os.environ["CIS_DYNAMODB_PERSON_TABLE"] = self.table_name

    def test_vault_populated(self):
        table_name = self.table_name
        fake_dynamo = boto3.resource('dynamodb', endpoint_url='http://localhost:4567')
        fake_table = fake_dynamo.Table(table_name)
        p = IdentityVault(table_name)
        p.table = fake_table
        res = p.all
        assert res is not None

    def test_data_classification(self):
        d = DataClassification('read:email')
        assert d.attributes is not None
        assert d.attributes[0] == 'primaryEmail'

        d = DataClassification('read:profile')
        read_profile_list = []
        read_profile_list.append('active')
        read_profile_list.append('authoritativeGroups')
        read_profile_list.append('created')
        read_profile_list.append('displayName')
        read_profile_list.append('firstName')
        read_profile_list.append('groups')
        read_profile_list.append('emails')
        read_profile_list.append('lastModified')
        read_profile_list.append('lastName')
        read_profile_list.append('nicknames')
        read_profile_list.append('PGPFingerprints')
        read_profile_list.append('phoneNumbers')
        read_profile_list.append('picture')
        read_profile_list.append('preferredLanguage')
        read_profile_list.append('primaryEmail')
        read_profile_list.append('shirtSize')
        read_profile_list.append('SSHFingerprints')
        read_profile_list.append('tags')
        read_profile_list.append('timezone')
        read_profile_list.append('uris')
        read_profile_list.append('user_id')
        read_profile_list.append('userName')

        for attr in read_profile_list:
            assert attr in d.attributes

    def test_can_find_user_in_vault(self):
        table_name = self.table_name
        fake_dynamo = boto3.resource('dynamodb', endpoint_url='http://localhost:4567')
        fake_table = fake_dynamo.Table(table_name)
        p = IdentityVault(table_name, 'read:profile')
        p.table = fake_table
        res = p.all

        dummy_random_user = random.choice(res)
        user_record = p.find(user_id=dummy_random_user.get('user_id'))
        assert user_record.get('groups') is not None

    def test_vault_returns_all(self):
        table_name = self.table_name
        fake_dynamo = boto3.resource('dynamodb', endpoint_url='http://localhost:4567')
        fake_table = fake_dynamo.Table(table_name)
        p = IdentityVault(table_name, 'read:profile')
        p.table = fake_table
        res = p.all
        assert res is not None

    def tearDown(self):
        v = FakeVault(self.table_name)
        v.delete()
        while v.is_ready is True:
            pass

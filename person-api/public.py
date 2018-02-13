"""Search operations in the identity vault."""
import boto3
import config
import logging


logger = logging.getLogger(__name__)
CONFIG = config.get_config()


class PublicData(object):
    def __init__(self, boto_session=None, scope=None):
        self.boto_session = boto_session
        self.dynamodb_resource = None
        self.table = None
        self.scope = scope

    def authenticate(self):
        self._get_boto_session()
        self._get_dynamodb_resource()
        self._get_dynamo_table()

    def create_or_update(self, public_user_data):
        if self.table is None:
            self.authenticate()

        response = self.table.put_item(
            Item=public_user_data
        )

    def find(self, email):
        """Search for a user record by ID and return."""
        user_email = {'user_email': email}
        if self.table is None:
            self.authenticate()

        response = self.table.get_item(
            Key=user_email
        )

        if response.get('Item') is not None:
            return response.get('Item')
        else:
            return {}

    def _get_boto_session(self):
        if self.boto_session is None:
            self.boto_session = boto3.session.Session(region_name='us-west-2')
        return self.boto_session

    def _get_dynamodb_resource(self):
        if self.dynamodb_resource is None:
            self.dynamodb_resource = self.boto_session.resource('dynamodb')
        return self.dynamodb_resource

    def _get_dynamo_table(self):
        if self.table is None:
            self.table = self.dynamodb_resource.Table(self._get_table_name())

    def _get_table_name(self):
        return CONFIG('public_data', namespace='cis')

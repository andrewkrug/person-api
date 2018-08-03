import boto3
import config
import json


CONFIG = config.get_config()


class PublicData(object):
    def __init__(self, boto_session=None):
        self.boto_session = boto_session
        self.dynamodb_resource = None
        self.table = None

    def authenticate(self):
        self._get_boto_session()
        self._get_dynamodb_resource()
        self._get_dynamo_table()

    def find(self, email):
        """Search for a user record by email and return."""
        email = {'user_email': email.lower()}

        self.authenticate()
        response = self.table.get_item(
            Key=email
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
        return CONFIG('public_data_table', namespace='cis')

def email_address(event):
    path = event.get('path')
    parameter = path.get('email')
    return parameter

def handler(event=None, context={}):
    p = PublicData()
    res = p.find(email_address(event))

    return json.dumps(res)

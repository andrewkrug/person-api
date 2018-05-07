"""Search operations in the identity vault."""
import boto3
import logging

from person_api import config

logger = logging.getLogger(__name__)
CONFIG = config.get_config()

class DataClassification(object):
    def __init__(self, scope):
        self.scope = scope

    @property
    def attributes(self):
        attrs = []
        if 'read:email' in self.scope:
            attrs.append('primaryEmail')
            pass
        elif 'read:profile' in self.scope:
            attrs.append('active')
            attrs.append('authoritativeGroups')
            attrs.append('created')
            attrs.append('displayName')
            attrs.append('firstName')
            attrs.append('groups')
            attrs.append('emails')
            attrs.append('lastModified')
            attrs.append('lastName')
            attrs.append('nicknames')
            attrs.append('PGPFingerprints')
            attrs.append('phoneNumbers')
            attrs.append('picture')
            attrs.append('preferredLanguage')
            attrs.append('primaryEmail')
            attrs.append('shirtSize')
            attrs.append('SSHFingerprints')
            attrs.append('tags')
            attrs.append('timezone')
            attrs.append('uris')
            attrs.append('user_id')
            attrs.append('userName')
        else:
            # Assume anonymous someday this might matter...
            pass
        return attrs


class IdentityVault(object):
    def __init__(self, boto_session=None, scope=None):
        self.boto_session = boto_session
        self.dynamodb_resource = None
        self.table = None
        self.scope = scope

    def authenticate(self):
        self._get_boto_session()
        self._get_dynamodb_resource()
        self._get_dynamo_table()

    @property
    def all(self):
        if self.table is None:
            self.authenticate()

        response = self.table.scan(
                AttributesToGet=[
                    'user_id',
                    'active',
                    'emails',
                    'primaryEmail',
                    'groups'
                ]
            )

        users = response.get('Items')

        while 'LastEvaluatedKey' in response:
            response = self.table.scan(
                AttributesToGet=[
                    'user_id',
                    'active',
                    'emails',
                    'primaryEmail',
                    'groups'
                ],
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            users.extend(response['Items'])

        return users

    def find(self, user_id):
        """Search for a user record by ID and return."""
        user_key = {'user_id': user_id}

        self.authenticate()
        response = self.table.get_item(
            Key=user_key,
            AttributesToGet=self._get_attr_for_scope()
        )

        if response.get('Item') is not None:
            return response.get('Item')
        else:
            return {}

    def _get_attr_for_scope(self):
        d = DataClassification(self.scope)
        return d.attributes

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
        return CONFIG('dynamodb_table', namespace='cis')

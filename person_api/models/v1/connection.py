import boto3
from flask import request
from flask import jsonify
from flask.views import MethodView

from person_api.config import get_config
from person_api.idp import requires_auth
from person_api.idp import requires_scope


class ConnectionAPI(MethodView):
    # Set to require a valid JWT
    # decorators = [requires_auth]
    def __init__(self):
        self.boto_session = None
        self.dynamodb_resource = None
        self.table = None
        self.environment = self._get_environment()

    def _get_environment(self):
        CONFIG = get_config()
        return CONFIG('environment', default='local')

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
        CONFIG = get_config()
        return CONFIG('public-data-table', namespace='cis', default='fake-cis-public-data-v1')

    def _connect_local_dynamo(self):
        self.boto_session = 'fake-session'
        self.dynamodb_resource = boto3.resource('dynamodb', endpoint_url='http://localhost:4567/')
        self.table = self.dynamodb_resource.Table(self._get_table_name())

    def get(self, user_email=None):

        if self.environment == 'local':
            self._connect_local_dynamo()
        else:
            self._get_boto_session()
            self._get_dynamodb_resource()
            self._get_dynamo_table()

        if request.args.get('nextPage'):
            return jsonify(self.get_page(request.args.get('nextPage')))

        if user_email is None:
            return jsonify(self.all())

        return jsonify(self.find(user_email))

    def find(self, user_email):
        """Search for a user record by email and return."""
        email = {'user_email': user_email}

        response = self.table.get_item(
            Key=email
        )

        if response.get('Item') is not None:
            return response.get('Item')
        else:
            return {}

    def get_page(self, esk):
        if self.environment == 'local':
            self._connect_local_dynamo()
        else:
            self._get_boto_session()
            self._get_dynamodb_resource()
            self._get_dynamo_table()

        response = self.table.scan(Limit=10, ExclusiveStartKey={'user_email': esk})

        if response.get('LastEvaluatedKey'):
            enriched_response = {
                'nextPage': response.get('LastEvaluatedKey'),
                'Items': response.get('Items', [])
            }

            return enriched_response

        if response.get('Items') is not None:
            return { 'Items': response.get('Items') }
        else:
            return {}

    def all(self):
        if self.environment == 'local':
            self._connect_local_dynamo()
        else:
            self._get_boto_session()
            self._get_dynamodb_resource()
            self._get_dynamo_table()

        response = self.table.scan(Limit=10)

        enriched_response = {
            'nextPage': response.get('LastEvaluatedKey'),
            'Items': response.get('Items', [])
        }

        if response.get('Items') is not None:
            return enriched_response
        else:
            return {}

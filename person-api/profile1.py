import boto3
import idp
import json
import logging
import urllib

import vault


logger = logging.getLogger(__name__)


"""
Event information that we care about parsing.
{
    'body': {},
    'method': 'GET',
    'headers': {
        'Accept': '*/*',
        'Authorization': 'Bearer ',
        },
        'query': {},
        'path': {'authzero_id': 'foo'},
        'identity': {
            'sourceIp': '162.244.37.195',
            'userAgent': 'curl/7.54.0',
        },
        'stageVariables': {}
}
"""

class Query(object):
    def __init__(self, event):
        self.event = event

    @property
    def user_id(self):
        path = self.event.get('path')
        parameter = path.get('authzero_id')
        return urllib.parse.unquote(parameter)

    @property
    def token(self):
        headers = self.event.get('headers')
        bearer_token = headers.get('Authorization').split(' ')[1]
        return bearer_token

    @property
    def scope(self):
        token = self.token
        party = idp.TrustedParty()
        trust = idp.Trust()
        scope = trust.verify(token, party.public_key).get('scope')
        return scope


def handler(event, context):

    # Parse this event into the requisite bits and bobs.
    q = Query(event)

    # Extract the bits we care about.
    user_id = q.user_id

    print(user_id)

    scope = q.scope

    # New up a boto session
    boto_session = boto3.session.Session(region_name='us-west-2')

    # Create a vault object and hand off the scope so it can do the right thing.
    id_vault = vault.IdentityVault(
        boto_session,
        scope
    )

    result = id_vault.find(user_id)

    if result is not None:
        # Return a response with the userdata.
        response = {
            "statusCode": 200,
            "body": json.dumps(result)
        }
    elif result is None:
        response = {
            "statusCode": 404,
            "body": json.dumps({})
        }
    else:
        response = {
            "statusCode": 500,
            "body": json.dumps({})
        }

    return response

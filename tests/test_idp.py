import logging
import unittest

from datetime import datetime
from datetime import timedelta
from jose import jws

from tests.fake_auth0 import FakeBearer
from tests.fake_auth0 import json_form_of_pk
from person_api import api
from unittest.mock import patch


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s:%(levelname)s:%(name)s:%(message)s'
)


class IdpTest(unittest.TestCase):
    def test_generate_fake_bearer_without_scope(self):
        f = FakeBearer()
        token = f.generate_bearer_without_scope()
        is_valid_sig = jws.verify(token, f.fake_signing_key_public, ['RS256'])
        assert is_valid_sig is not None
        assert token is not None

    def test_generate_fake_bearer_with_scope(self):
        f = FakeBearer()
        token = f.generate_bearer_with_scope('read:profile')
        is_valid_sig = jws.verify(token, f.fake_signing_key_public, ['RS256'])
        assert is_valid_sig is not None
        assert token is not None

    @patch('person_api.idp.get_jwks')
    def test_get_token_auth_header(self, fake_jwks):
        f = FakeBearer()
        fake_jwks.return_value = json_form_of_pk
        token = f.generate_bearer_without_scope()
        api.app.testing = True
        self.app = api.app.test_client()
        result = self.app.post(
            '/api/private',
            headers={
                'Authorization': 'Bearer ' + token
            },
            follow_redirects=True
        )
        assert result.status_code == 200
        assert result.data == b'{\n  "message": "Hello from a private endpoint!"\n}\n'

    @patch('person_api.idp.get_jwks')
    def test_private_endpoint_with_scope(self, fake_jwks):
        f = FakeBearer()
        fake_jwks.return_value = json_form_of_pk
        token = f.generate_bearer_with_scope('read:profile')
        api.app.testing = True
        self.app = api.app.test_client()
        result = self.app.post(
            '/api/private-scoped',
            headers={
                'Authorization': 'Bearer ' + token
            },
            follow_redirects=True
        )
        assert result.status_code == 200
        assert result.data == b'{\n  "message": "Hello from a scoped private endpoint!"\n}\n'

    @patch('person_api.idp.get_jwks')
    def test_access_denied_for_bad_aud(self, fake_jwks):
        f = FakeBearer()
        fake_jwks.return_value = json_form_of_pk
        bad_claims = {
            'iss': 'https://auth-dev.mozilla.auth0.com/',
            'sub': 'mc1l0G4sJI2eQfdWxqgVNcRAD9EAgHib@clients',
            'aud': 'https://hacksforpancakes',
            'iat': (datetime.utcnow() - timedelta(seconds=3100)).strftime('%s'),
            'exp': (datetime.utcnow() - timedelta(seconds=3100)).strftime('%s'),
            'scope': 'read:profile',
            'gty': 'client-credentials'
        }

        token = f.generate_bearer_with_scope('read:profile', bad_claims)
        api.app.testing = True
        self.app = api.app.test_client()
        result = self.app.post(
            '/api/private-scoped',
            headers={
                'Authorization': 'Bearer ' + token
            },
            follow_redirects=True
        )
        assert result.status_code == 401

    @patch('person_api.idp.get_jwks')
    def test_access_denied_for_expired_token(self, fake_jwks):
        f = FakeBearer()
        fake_jwks.return_value = json_form_of_pk
        bad_claims = {
            'iss': 'https://auth-dev.mozilla.auth0.com/',
            'sub': 'mc1l0G4sJI2eQfdWxqgVNcRAD9EAgHib@clients',
            'aud': 'https://hacksforpancakes',
            'iat': (datetime.utcnow() + timedelta(seconds=3100)).strftime('%s'),
            'exp': (datetime.utcnow() + timedelta(seconds=3100)).strftime('%s'),
            'scope': 'read:profile',
            'gty': 'client-credentials'
        }

        token = f.generate_bearer_with_scope('read:profile', bad_claims)
        api.app.testing = True
        self.app = api.app.test_client()
        result = self.app.post(
            '/api/private-scoped',
            headers={
                'Authorization': 'Bearer ' + token
            },
            follow_redirects=True
        )
        assert result.status_code == 401


    @patch('person_api.idp.get_jwks')
    def test_access_denied_for_incorrect_scope(self, fake_jwks):
        f = FakeBearer()
        fake_jwks.return_value = json_form_of_pk
        bad_claims = {
            'iss': 'https://auth-dev.mozilla.auth0.com/',
            'sub': 'mc1l0G4sJI2eQfdWxqgVNcRAD9EAgHib@clients',
            'aud': 'https://person-api.sso.allizom.org',
            'iat': (datetime.utcnow() - timedelta(seconds=3100)).strftime('%s'),
            'exp': (datetime.utcnow() - timedelta(seconds=3100)).strftime('%s'),
            'scope': 'read:allthething',
            'gty': 'client-credentials'
        }

        token = f.generate_bearer_with_scope('read:profile', bad_claims)
        api.app.testing = True
        self.app = api.app.test_client()
        result = self.app.post(
            '/api/private-scoped',
            headers={
                'Authorization': 'Bearer ' + token
            },
            follow_redirects=True
        )
        assert result.status_code == 403

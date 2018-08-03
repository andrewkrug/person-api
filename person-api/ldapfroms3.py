"""Object for fetching ldap data from kangsterizers ldap2s3 connector."""
import config
import boto3
import json
import os
import sys
import lzma

CONFIG = config.get_config()

class People(object):
    def __init__(self):
        self.s3 = None

    def connect(self):
        """Returns an s3 bucket resource for a bucket."""
        s3_region = CONFIG('ldap_s3_region', namespace='temporary')
        s3_bucket = CONFIG('ldap_diff_bucket', namespace='temporary')

        boto_session = boto3.session.Session(region_name=s3_region)
        s3 = boto_session.resource('s3')
        self.s3 = s3.Bucket(s3_bucket)

        return self.s3

    @property
    def all(self):
        return self._get_ldap_json()

    def _get_ldap_json(self):
        if self.s3 is None:
            self.connect()

        object_key = '{}'.format(
            CONFIG('ldap_json_file', namespace='temporary')
        )

        self.s3.download_file(object_key, '/tmp/{}'.format(object_key))

        ldap_json = json.loads(
            lzma.open('/tmp/{}'.format(object_key)).read()
        ).items()

        return ldap_json

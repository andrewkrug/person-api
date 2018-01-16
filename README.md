# Mozilla Change Integration Service PersonAPI

This is a proof of concept.  Not ready for use outside of Core IAM team.

__Description:__

This API will return profiles as they are stored in the dynamodb table.  Currently only two scopes for non
interactive clients are supported.  But more scopes and search features are planned for the future.

# Deployment Container

```
docker run --rm -ti \
-v ~/.aws:/root/.aws \
-v ~/workspace/person-api/:/workspace \
mozillaiam/docker-sls:latest \
/bin/bash

npm install serverless-domain-manager --save-dev
npm install serverless-python-requirements --save-dev
```

# Locations
Highly subject to change.

__Prod__ : https://person-api.sso.mozilla.com/v1/profile/
__Dev__ : https://person-api.sso.allizom.org/v1/profile/

__Scopes Supported:__
  - read:email
  - read:profile

# Calling the Profile Endpoint

 curl --request GET --url https://person-api.sso.allizom.org/v1/profile/ad%7CMozilla-LDAP-Dev%7Ckangtest --header 'authorization: Bearer YOURBEARERTOKENHERE'

> Make sure you urlencode the authzero_id.

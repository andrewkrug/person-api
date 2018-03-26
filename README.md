# Mozilla Change Integration Service: PersonAPI

This API return user profile data from the [Change Integration Service](https://github.com/mozilla-iam/cis) dynamodb table.

## For PersonAPI Users
### API Locations

- **Prod** : https://person-api.sso.mozilla.com/{api-version}/
- **Dev** : https://person-api.sso.allizom.org/{api-version}/

### Scopes

- `read:email`: access user's `primaryEmail`
- `read:profile`: access all user profile data
- No scope/public: access user's supported connections data (this is mainly used for the [login
window](https://github.com/mozilla-iam/auth0-custom-lock))

### Endpoints

> You will need to acquire an access token (also called bearer token) in order to access this API.
> The access token is valid for a limited amount of time and can be obtained by exchanging credentials with our OAuth2 API
> authorizer.
> When the access token expire, it must be renewed in order to continue using the API.
> 
> See <https://github.com/mozilla-iam/mozilla-iam/> for more information about how to obtain IAM credentials.

#### GET `/v1/profile/{user_id}`

**Scope**: `read:profile`

Returns the complete user profile

**Example**:
```
curl --request GET --url https://person-api.sso.allizom.org/v1/profile/ad%7CMozilla-LDAP-Dev%7Ckangtest --header 'authorization: Bearer YOURBEARERTOKENHERE'
```

*Make sure you urlencode the `user_id` parameter.*

#### GET `/v1/connection/{email}`

Returns the valid connections for the user (such as "ad", "github", etc.)

**Scope**: None

**Example**:
```
curl --request GET --url https://person-api.sso.allizom.org/v1/connection/gdestuynder@mozilla.com
```

## For IAM Developers
### Deployment How-to

```
docker run --rm -ti \
-v ~/.aws:/root/.aws \
-v ~/workspace/person-api/:/workspace \
mozillaiam/docker-sls:latest \
/bin/bash

npm install serverless-domain-manager --save-dev
npm install serverless-python-requirements --save-dev
```

### API Endpoint Setup

API endpoints are setup in `serverless.yml` in the `functions` section.

**Example**:

```
...
functions:
  profilePublicConnectionMethod:
    # Calls `connection1.py`
    handler: connection1.handler
    events:
      - http:
          # Actual endpoint
          path: v1/connection/{email}
          method: get
...
          request:
            parameters:
              paths:
                email: true
...
```

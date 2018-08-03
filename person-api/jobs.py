"""Populate data for connection method table periodically."""

# XXX TBD deprecate this by redesigning the vault schema.
# XXX TBD develop process for backup and restore of current vault.

import boto3
import ldapfroms3
import logging
import public
import utils
import vault

logger = logging.getLogger(__name__)

sl = utils.StructuredLogger(
    name=__name__,
    level=logging.INFO
)

def _get_connection_method(user):
    if user.get('primaryEmail').split('@')[1] == 'mozilla.com':
        return 'ad'
    elif 'mozilliansorg_nda' in user.get('groups'):
        return 'github'
    else:
        return user.get('user_id').split('|')[0]

def _generate_public_struct(user):
    public_user_data = {
        'user_email': user.get('primaryEmail'),
        'connection_method': _get_connection_method(user)
    }

    return public_user_data

def _score_security(connection_method):
    scores = {'email': 10, 'google': 20, 'github': 30, 'ad': 40}
    return scores.get(connection_method, 0)

def _is_more_secure(public_user_data, pdt):
    user_exists = pdt.find(public_user_data.get('user_email'))

    if user_exists:
        connection_method = user_exists.get('connection_method')

        if _score_security(public_user_data.get('connection_method')) > _score_security(connection_method):
            return True
        else:
            return False
    else:
        return True


def populate_public_table(event=None, context={}):
    idv = vault.IdentityVault()
    pdt = public.PublicData()

    logger.info('Scanning identity vault for all users.')
    all_users = idv.all

    logger.info('The number of users in the vault is: {}'.format(len(all_users)))

    for user in all_users:
        if user.get('primaryEmail') is not None:
            public_user_data = _generate_public_struct(user)
            logger.info('Storing the data in vault for: {}'.format(public_user_data))
            if _is_more_secure(public_user_data, pdt):
                res = pdt.create_or_update(public_user_data)
                logger.info('Result of storage is: {}'.format(res))
            else:
                pass

    # XXX TBD Trust LDAP json file inherently until LDAP publisher exists.
    logger.info('Pulling in temporary data from LDAP.')
    ldap_people = ldapfroms3.People().all

    for k, v in ldap_people:
        email = v.get('primaryEmail')

        if email is not None:
            public_user_data = {
                'user_email': email.lower(),
                'connection_method': 'ad'
            }
            res = pdt.create_or_update(public_user_data)
            logger.info('Result of storage is: {}'.format(res))
        else:
            pass

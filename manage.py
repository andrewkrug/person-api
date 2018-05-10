import argparse

from tests import fake_cis_v1

parser = argparse.ArgumentParser()
parser.add_argument("--createdb", help="Create all the dynamo db tables for identity vault v1 and v2.", action="store_true")
parser.add_argument("--seed", help="Seed the identity vault with fixture users.", action="store_true")
parser.add_argument("--dropdb", help="Drop all the databases.", action="store_true")

args = parser.parse_args()

if args.createdb:
    fake_vault = fake_cis_v1.FakeVault(table_name='fake-vault-v1')
    fake_connections = fake_cis_v1.FakeConnectionTable(table_name='fake-cis-public-data-v1')
    fake_vault.find_or_create()
    fake_connections.find_or_create()
    print('The tables have been created.')

if args.dropdb:
    fake_vault = fake_cis_v1.FakeVault(table_name='fake-vault-v1')
    fake_connections = fake_cis_v1.FakeConnectionTable(table_name='fake-cis-public-data-v1')
    fake_vault.delete()
    fake_connections.delete()
    print('The tables have been delete.')

if args.seed:
    fake_vault = fake_cis_v1.FakeVault(table_name='fake-vault-v1')
    fake_connections = fake_cis_v1.FakeConnectionTable(table_name='fake-cis-public-data-v1')
    fake_vault.populate()
    fake_connections.populate()
    print('The tables have been seeded with user info.')

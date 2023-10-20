# Copyright (c) HashiCorp, Inc.
# SPDX-License-Identifier: MPL-2.0

import hvac
import sys

# Authentication
client = hvac.Client(
    url='https://vault-cluster-public-vault-8c5404c4.dbd71e51.z1.hashicorp.cloud:8200',
    token='hvs.CAESIMallB0-PERRzkm_WGnRdZH_Tl9mbyAcStYFXIUeabOxGicKImh2cy5scUxtMFdyOWZaZlRJcU9lTFlhSGI2REcuVDJhbjcQjAE',
    namespace='admin'  # If namespace is configured, make sure to set here
)
#
# Writing a secret in the default secret engine
create_response = client.secrets.kv.v2.create_or_update_secret(
    path='my-secret-password',
    secret=dict(password='Hashi123'),
)

print('Secret written successfully.')

# Reading a secret
read_response = client.secrets.kv.v1.read_secret(path='kimone', mount_point='cubbyhole')
#
print(read_response)
# password = read_response['data']['name']['name']
password = read_response['data']
print(password['name'])

# if password != 'kiki':
#     sys.exit('unexpected password')

# print('Access granted!')

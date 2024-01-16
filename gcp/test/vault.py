# # Copyright (c) HashiCorp, Inc.
# # SPDX-License-Identifier: MPL-2.0
#
# import hvac
# import sys
#
# # Authentication
# client = hvac.Client(
#     url=<>,
#     token=<>,
#     namespace='admin'
# )
#
# read_response = client.secrets.kv.v2.read_secret(path='cubbyhole/test/webapp')
# print(read_response)
# # Writing a secret
# # create_response = client.secrets.kv.v2.create_or_update_secret(
# #     path='my-secret-password',  mount_point='kv',
# #     secret=dict(password='Hashi123'),
# # )
#
# print('Secret written successfully.')

# import hvac
#
# client = hvac.Client(url='https://sample-cluster-public-vault-cc9280b1.814fec76.z1.hashicorp.cloud:8200')
#
# def init_server():
#     print(f" Is client authenticated: {client.is_authenticated()}")
#
# def write_secret():
#
#     create_response = client.secrets.kv.v2.create_or_update_secret(path='hello', secret=dict(foo="bar"))
#
#     print(create_response)
#
#
# def read_secret():
#     read_response = client.secrets.kv.v2.read_secret_version(path='kv/foo')
#
#     print(read_response)
#
# if __name__ == "__main__":
#     # client.secrets.
#     # write_secret()
#     read_secret()
#     # init_server()

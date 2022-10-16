import sys
from google.cloud import secretmanager

client_secret_manager = secretmanager.SecretManagerServiceClient()


def download(project_number):
    # Create GCP managed secret: https://console.cloud.google.com/security/secret-manager
    # Make sure to select upload file option, and upload your local copy of settings.toml
    name_medium_secret = "projects/{}/secrets/tap_settings_files/versions/latest".format(project_number)
    response = client_secret_manager.access_secret_version(name=name_medium_secret)
    pwd = response.payload.data.decode("UTF-8")
    with open('settings.toml', 'w') as outfile:
        outfile.write(pwd)


def upload(project_number):
    # Build the resource name of the parent secret.
    parent = client_secret_manager.secret_path(project_number, 'tap_settings_files')
    with open('settings.toml', 'r') as outfile:
        payload = outfile.read().encode("UTF-8")
        response = client_secret_manager.add_secret_version(request={"parent": parent, "payload": {"data": payload}})
        print(response)


if __name__ == "__main__":
    method = sys.argv[1]
    method_argument = sys.argv[2]
    if str(method) == 'download' and method_argument:
        download(str(method_argument))
    elif str(method) == 'upload' and method_argument:
        upload(str(method_argument))


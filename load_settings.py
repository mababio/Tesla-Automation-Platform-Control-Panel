import sys
from google.cloud import secretmanager

client_secret_manager = secretmanager.SecretManagerServiceClient()

# Create GCP managed secret: https://console.cloud.google.com/security/secret-manager
# Make sure to select upload file option, and upload your local copy of settings.toml
NAME_MEDIUM_SECRET = "projects/{}/secrets/tap_settings_files/versions/latest".format(sys.argv[1])
response = client_secret_manager.access_secret_version(name=NAME_MEDIUM_SECRET)
pwd = response.payload.data.decode("UTF-8")
with open('settings.toml', 'w') as outfile:
    outfile.write(pwd)

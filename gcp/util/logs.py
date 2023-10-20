import logging
# Imports the Cloud Logging client library
import google.cloud.logging
# from google.oauth2 import service_account
logger = logging.getLogger(__name__)
FORMAT = "[%(asctime)s %(filename)s->%(funcName)s():%(lineno)s]%(levelname)s: %(message)s"
logging.basicConfig(format=FORMAT)
logger.setLevel(logging.DEBUG)

# credentials = service_account.Credentials.from_service_account_file(
#     '../github_action.json')


# Instantiates a client
client = google.cloud.logging.Client()
# Retrieves a Cloud Logging handler based on the environment
# you're running in and integrates the handler with the
# Python logging module. By default this captures all logs
# at INFO level and higher
client.setup_logging()
#
# def tomm(attempts, delay):
#     print('logged error')

import requests
import os

TESLA_DATA_SERVICES_BASE_URL = os.environ.get("TESLA_DATA_SERVICES_BASE_URL")


def get_car_document():
    """
    Gets Mongodb document that represents the state of car. Database request is handled by Fast API
    :return: JSON object representing MongoDb Car document
    """
    sess = requests.Session()
    adapter = requests.adapters.HTTPAdapter(max_retries=20)
    sess.mount('https://', adapter)
    return requests.get(f"{TESLA_DATA_SERVICES_BASE_URL}/api/car/get/car").json()


def set_car_document(param, value=None):
    sess = requests.Session()
    adapter = requests.adapters.HTTPAdapter(max_retries=20)
    sess.mount('https://', adapter)
    if value is not None:
        return requests.put(f"{TESLA_DATA_SERVICES_BASE_URL}/api/car/update/{param}/{value}")
    else:
        return requests.put(f"{TESLA_DATA_SERVICES_BASE_URL}/api/car/update/{param}")

import requests

from config import settings


def get_car_document():
    """
    Gets Mongodb document that represents the state of car. Database request is handled by Fast API
    :return: JSON object representing MongoDb Car document
    """
    sess = requests.Session()
    adapter = requests.adapters.HTTPAdapter(max_retries=20)
    sess.mount('https://', adapter)
    # url_tesla_data_services = f"{settings['production']['URL']['tesla_data_services']}/api/car"
    url_tesla_data_services = "http://tesla-data-services:8085/api/car"
    return requests.get(f"{url_tesla_data_services}/get/car").json()



def set_car_document(param, value=None):
    sess = requests.Session()
    adapter = requests.adapters.HTTPAdapter(max_retries=20)
    sess.mount('https://', adapter)
    url_tesla_data_services = settings['production']['URL']['tesla_data_services'] + '/api/car'
    if value is not None:
        return requests.put(f"{url_tesla_data_services}/update/{param}/{value}")
    else:
        return requests.put(f"{url_tesla_data_services}/update/{param}")
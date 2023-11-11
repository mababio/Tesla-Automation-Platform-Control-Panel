import json
from retry import retry
from logs import logger
import notification as chanify
from enum import Enum
import requests
import os


class TeslaMode(Enum):
    HOME = 0
    AWAY = 1
    VACATION = 2
    IN_SERVICE = 3


class Tesla:

    def __init__(self):
        self.TESLA_LOCATION_SERVICES_BASE_URL = os.environ.get("TESLA_LOCATION_SERVICES_BASE_URL")
        self.TESLA_DATA_SERVICES_BASE_URL = os.environ.get("TESLA_DATA_SERVICES_BASE_URL")
        self.TESLA_CONTROL_SERVICES_BASE_URL = os.environ.get("TESLA_CONTROL_SERVICES_BASE_URL")
        self.HOME_STREET = os.environ.get("HOME_STREET")
        self.url_tesla_location_services = self.TESLA_LOCATION_SERVICES_BASE_URL
        self.proximity_value = None
        self.sess = requests.Session()
        adapter = requests.adapters.HTTPAdapter(max_retries=20)
        self.sess.mount('https://', adapter)
        self.url_tesla_data_services = f'{self.TESLA_DATA_SERVICES_BASE_URL}/api/car'

    def is_tesla_moving(self):
        try:
            return False if self.sess.get(self.url_tesla_location_services, json={'method': 'get_location'}).json()[
                                'speed'] is None else True
        except Exception as e:
            logger.error('is_tesla_moving:::: Issue with tesla location Google function  {}'.format(str(e)))
            chanify.send_push_notification(
                'is_tesla_moving:::: Issue with tesla location Google function {} '.format(str(e)))
            raise

    @retry(logger=logger, delay=15, tries=2, backoff=2)
    def is_near(self):
        return_value = self.get_proximity()
        self.proximity_value = return_value['difference']
        if return_value['is_on_arcuri'] and return_value['is_close']:
            # self.db.set_tesla_location_is_home_value(True)
            self.sess.put(self.url_tesla_data_services + "/update/is_near/{}".format(True))
            return True
        else:
            return False

    @retry(logger=logger, delay=10, tries=3, backoff=2)
    def get_proximity(self, param_prox=None):
        if param_prox is None:
            param_prox = self.get_location()
        if isinstance(param_prox, dict):
            try:
                response_obj = self.sess.get(self.url_tesla_location_services, json={'method': 'get_proximity'})
                response_obj.raise_for_status()
                return response_obj.json()
            except Exception as e:
                logger.error('get_proximity: tesla prox function error {}'.format(str(e)))
                raise
        else:
            raise TypeError('get_location GCP function return something other than dict')

    @retry(logger=logger.error("GET_LOCATION FAILED: RERUNNING"), delay=10, tries=10, backoff=2)
    def get_location(self):
        try:
            response_obj = requests.get(self.url_tesla_location_services, json={'method': 'get_location'})
            response_obj.raise_for_status()
            r_location = response_obj.json()
        except Exception as e:
            logger.error('Connection issue with {} : {}'.format(self.url_tesla_location_services, str(e)))
            chanify.send_push_notification(
                'Connection issue with {}'.format(self.url_tesla_location_services + ":" + str(e)))
            raise

        if len(r_location) == 0:
            logger.warning('get_location ::::: Tesla API is not providing Vehicle data right now')
            chanify.send_push_notification('get_location ::::: Tesla API is not providing Vehicle data right now')
            car_document = self.sess.get('{}{}'.format(self.url_tesla_data_services, '/get/car'))
            r_location = car_document['gps']
        try:
            self.sess.put('{}{}'.format(self.url_tesla_data_services, '/update/gps'), json=json.dumps(r_location))
            # self.db.save_location(r_location)
        except Exception as e:
            logger.error("Issue with saving latlon to mongodb:" + str(e))
            chanify.send_push_notification("Issue with  saving latlon to mongodb:" + str(e))
            raise
        return r_location

    @retry(logger=logger, delay=2, tries=3)
    def is_on_home_street(self):
        try:
            return requests.get(f'{self.TESLA_LOCATION_SERVICES_BASE_URL}/is_home_street')
        except Exception as e:
            chanify.send_push_notification(f'Issue getting is_home_street value: {e}')


if __name__ == "__main__":
    obj = Tesla()
    print(obj.is_near())
    print('all done')

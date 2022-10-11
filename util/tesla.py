import requests
from retry import retry
import googlemaps
import util.db_mongo as db_mongo
from util.logs import logger
import util.notification as chanify
from enum import Enum
from config import settings


class TeslaMode(Enum):
    HOME = 0
    AWAY = 1
    VACATION = 2
    IN_SERVICE = 3


class Tesla:

    def __init__(self):
        self.gmaps = googlemaps.Client(key=settings['production']['key']['gmaps'])
        self.url_tesla_prox = settings['production']['URL']['tesla_prox']
        self.url_tesla_location = settings['production']['URL']['tesla_location']
        self.proximity_value = None
        self.db = db_mongo.DBClient()

    def is_tesla_moving(self):
        try:
            return False if requests.post(self.url_tesla_location).json()['speed'] is None else True
        except Exception as e:
            logger.error('is_tesla_moving:::: Issue with tesla location Google function ' + str(e))
            chanify.send_push_notification('is_tesla_moving:::: Issue with tesla location Google function ' + str(e))
            raise

    @retry(logger=logger, delay=10, tries=2, backoff=2)
    def is_close(self):
        return_value = self.get_proximity()
        self.proximity_value = return_value['difference']
        if return_value['is_on_arcuri'] and return_value['is_close']:
            self.db.set_tesla_location_is_home_value(True)
            return True
        else:
            return False

    @retry(logger=logger, delay=10, tries=2, backoff=2)
    def get_proximity(self):
        param_prox = self.get_location()
        if isinstance(param_prox, dict):
            try:
                return requests.post(self.url_tesla_prox, json=param_prox).json()
            except Exception as e:
                logger.error('get_proximity: tesla prox function error')
                raise
        else:
            raise TypeError('get_location GCP function return something other than dict')

    @retry(logger=logger, delay=10, tries=2, backoff=2)
    def get_location(self):
        try:
            r_location = requests.get(self.url_tesla_location).json()
        except Exception as e:
            logger.error('Connection issue with' + self.url_tesla_location + ":" + str(e))
            chanify.send_push_notification('Connection issue with' + self.url_tesla_location + ":" + str(e))
            raise
        try:
            lat = float(r_location['lat'])
            lon = float(r_location['lon'])
            param_prox = {"lat": lat, "lon": lon}
        except Exception as e:
            logger.warning('get_location latlon= values are not valid:' + str(e))
            chanify.send_push_notification('get_location latlon= values are not valid:' + str(e))
            raise
        try:
            self.db.save_location(r_location)
        except Exception as e:
            logger.error("Issue with saving latlon to mongodb:" + str(e))
            chanify.send_push_notification("Issue with  saving latlon to mongodb:" + str(e))
            raise
        return param_prox

    @retry(logger=logger, delay=2, tries=3)
    def is_on_home_street(self):
        latlon = self.get_location()
        try:
            reverse_geocode_result = self.gmaps.reverse_geocode((latlon['lat'], latlon['lon']))
        except Exception as e:
            logger.warning("is_on_home_street: Issue with Gmaps geocode:" + str(e))
            raise
        try:
            for i in reverse_geocode_result:
                if 'Arcuri Court' in i['address_components'][0]['long_name']:
                    return True
            return False
        except Exception as e:
            logger.warning("is_on_home_street: output of geocode is not as expected:" + str(e))
            raise


if __name__ == "__main__":
    obj = Tesla()
    print(requests.get(settings['production']['URL']['tesla_info']).json()['vehicle_state']['is_user_present'])
   #  # # print(obj.is_battery_good()) and self.is_parked
   #  # param_prox={'lat':40.669900, 'lon': -74.095629}
   #  param_prox={'lat':40.663205, 'lon': -74.074595}
   #  prox = requests.post('https://us-east4-ensure-dev-zone.cloudfunctions.net/function-tesla-prox', json=param_prox).json()
   #  print(prox)

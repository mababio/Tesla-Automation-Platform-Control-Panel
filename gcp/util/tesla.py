import requests
from retry import retry
import googlemaps
from gcp import util as db_mongo, util as chanify
from gcp.util.logs import logger
from enum import Enum
from gcp.config import settings


class TeslaMode(Enum):
    HOME = 0
    AWAY = 1
    VACATION = 2
    IN_SERVICE = 3


class Tesla:

    def __init__(self):
        self.gmaps = googlemaps.Client(key=settings['production']['key']['gmaps'])
        self.url_tesla_location_services = settings['production']['URL']['tesla_location_services']
        self.proximity_value = None
        self.db = db_mongo.DBClient()
        self.sess = requests.Session()
        adapter = requests.adapters.HTTPAdapter(max_retries=20)
        self.sess.mount('https://', adapter)

    def is_tesla_moving(self):
        try:
            return False if self.sess.post(self.url_tesla_location_services, json={'method': 'get_location'}).json()['speed'] is None else True
        except Exception as e:
            logger.error('is_tesla_moving:::: Issue with tesla location Google function  {}'.format(str(e)))
            chanify.send_push_notification('is_tesla_moving:::: Issue with tesla location Google function {} '.format(str(e)))
            raise

    @retry(logger=logger, delay=15, tries=2, backoff=2)
    def is_near(self):
        return_value = self.get_proximity()
        self.proximity_value = return_value['difference']
        if return_value['is_on_arcuri'] and return_value['is_close']:
            self.db.set_tesla_location_is_home_value(True)
            return True
        else:
            return False

    # @retry(logger=logger, delay=10, tries=2, backoff=2)
    def get_proximity(self, param_prox=None):
        if param_prox is None:
            param_prox = self.get_location()
        if isinstance(param_prox, dict):
            try:
                response_obj = self.sess.get(self.url_tesla_location_services, json={'method': 'get_proximity'})
                response_obj.raise_for_status()
                return response_obj.json()
            except Exception as e:
                logger.error('get_proximity: tesla prox function error')
                raise
        else:
            raise TypeError('get_location GCP function return something other than dict')

    @retry(logger=logger.error("GET_LOCATION FAILED: RERUNNING"), delay=10, tries=10, backoff=2)
    def get_location(self):
        try:
            response_obj = self.sess.post(self.url_tesla_location_services, json={'method': 'get_location'})
            response_obj.raise_for_status()
            r_location = response_obj.json()
        except Exception as e:
            logger.error('Connection issue with {} : {}'.format(self.url_tesla_location_services, str(e)))
            chanify.send_push_notification('Connection issue with {}'.format(self.url_tesla_location_services + ":" + str(e)))
            raise

        if len(r_location) == 0:
            logger.warning('get_location ::::: Tesla API is not providing Vehicle data right now')
            chanify.send_push_notification('get_location ::::: Tesla API is not providing Vehicle data right now')
            r_location = self.db.get_saved_location()

        lat = float(r_location['lat'])
        lon = float(r_location['lon'])
        param_prox = {"lat": lat, "lon": lon}
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
                if settings['tesla-location-services']['home_street'] in i['address_components'][0]['long_name']:
                    return True
            return False
        except Exception as e:
            logger.warning("is_on_home_street: output of geocode is not as expected: {}".format(str(e)))
            raise

    def unlock_tesla(self):
        if not self.is_tesla_moving():
            try:
                resposne_obj = self.sess.post(settings['production']['URL']['tesla_control'], json={"command": "UNLOCK_CAR"})
                if resposne_obj.status_code == 200:
                    chanify.send_push_notification("TESLA UNLOCK:::: Tesla request to unlock was sent")
                else:
                    chanify.send_push_notification('TESLA UNLOCK:::: RAN into HTTP issue')
                return resposne_obj.json()
            except Exception as e:
                logger.error("unlock_tesla::::: Issue with http request to :::: " +
                             settings['production']['URL']['tesla_control'] + str(e))
                raise


if __name__ == "__main__":
    obj = Tesla()
    print(obj.get_proximity())
    # 40.669949, -74.096796
    # print(obj.get_proximity({'lat': '40.669949', 'lon': '-74.096796'}))
    # print(obj.g)
    # print(self.sess.get(settings['production']['URL']['tesla_info']).json()['vehicle_state']['is_user_present'])
#  # # print(obj.is_battery_good()) and self.is_parked
#  # param_prox={'lat':40.669900, 'lon': -74.095629}
#  param_prox={'lat':40.663205, 'lon': -74.074595}
#  prox = self.sess.post('https://us-east4-ensure-dev-zone.cloudfunctions.net/function-tesla-prox', json=param_prox).json()
#  print(prox)
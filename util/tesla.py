import logging
import requests
from retry import retry
import googlemaps
import util.db_mongo as db_mongo
from util.logs import logger
import util.notification as chanify
from enum import Enum
from datetime import datetime
from pytz import timezone


class TeslaMode(Enum):
    HOME = 0
    AWAY = 1
    VACATION = 2
    IN_SERVICE = 3


class Tesla:

    def __init__(self):
        self.gmaps = googlemaps.Client(key='AIzaSyCpSgkND8wBAdlK8sSaqjgqFMPx7AJmq68')
        self.url_tesla_prox = "https://us-east4-ensure-dev-zone.cloudfunctions.net/function-tesla-prox"
        self.url_tesla_location = "https://us-east4-ensure-dev-zone.cloudfunctions.net/function-tesla-get_location"
        self.proximity_value = None
        self.url_tesla_set_temp = "https://us-east4-ensure-dev-zone.cloudfunctions.net/function-tesla-set-temp"
        self.url_tesla_info = "https://us-east4-ensure-dev-zone.cloudfunctions.net/tesla-info"
        self.db = db_mongo.DBClient()

    @retry(logger=logger, delay=10, tries=3)
    def set_temp(self, temp='22.7778'):
        try:
            param = {"temp": temp}
            return requests.post(self.url_tesla_set_temp, json=param)
        except Exception as e:
            logger.warning('Issue calling ' + str(self.url_tesla_set_temp) + ': ' + str(e))
            raise

    @retry(logger=logger, delay=10, tries=3)
    def is_battery_good(self):
        try:
            battery_range = requests.get(self.url_tesla_info).json()['charge_state']['battery_range']
            return True if battery_range > 100 else False
        except Exception as e:
            logger.warning('Issue calling ' + str(self.url_tesla_info) + ': ' + str(e))
            raise

    @retry(logger=logger, delay=10, tries=3)
    def is_in_service(self):
        try:
            return requests.get(self.url_tesla_info).json()['in_service']
        except Exception as e:
            logger.warning('Issue calling ' + str(self.url_tesla_info) + ': ' + str(e))

    @retry(logger=logger, delay=10, tries=3)
    def is_parked(self,length=5):
        shift_state = requests.get(self.url_tesla_info).json()['drive_state']['shift_state']
        db_latlon_age_mins = self.__get_db_latlon_age()
        return True if shift_state is None and db_latlon_age_mins > length else False

    def __get_db_latlon_age(self):
        est = timezone('US/Eastern')
        db_latlon_timestamp_est = self.db.tesla_database['tesla_location'].find_one({'_id':'current'})['timestamp'].split('.')[0]
        db_latlon_timestamp_est_str = str(db_latlon_timestamp_est)
        db_latlon_timestamp_datetime_obj = datetime.strptime(db_latlon_timestamp_est_str, "%Y-%m-%d %H:%M:%S")

        current_timestamp_est_datetime_obj = datetime.now(est)
        current_timestamp_est_datetime_obj_formatted = str(current_timestamp_est_datetime_obj).split('.')[0]
        accepted_current_timestamp_est_datetime_obj = datetime.strptime(current_timestamp_est_datetime_obj_formatted, "%Y-%m-%d %H:%M:%S")

        timelapse = accepted_current_timestamp_est_datetime_obj - db_latlon_timestamp_datetime_obj
        return int(timelapse.total_seconds()/60) # this is in mins

    def is_tesla_parked_long(self):
        if not self.is_in_service() and self.is_battery_good() and self.is_parked(): #and not self.is_on_home_street():
            chanify.send_push_notification('Yes works')
            return True
        else:
            return False



    # def is_tesla_ready_for_climate_on(self):
    # 1. car is not moving, and parked for a while
 #       - store gps location and add time_share timestamp if hasn't chnage then
    # 2. car is not home
    # 3. battery is good enough Done
    # 4. not in vacation mode - save to mongo Done
    # 5.  not in_service Done
    #     return True
    #
    #
    # def is_dog_in_car(self):
    #     return True
    def is_tesla_moving(self):
        speed = requests.post(self.url_tesla_location).json()['speed']
        if speed == 'None':
            return False
        else:
            return True

    @retry(logger=logger, delay=2, tries=2)
    def is_close(self):
        return_value = self.get_proximity()
        self.proximity_value = return_value['difference']
        return True if return_value['is_on_arcuri'] and return_value['is_close'] else False

    @retry(logger=logger, delay=0, tries=2)
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

    @retry(logger=logger, delay=10, tries=3)
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
        return param_prox

    # def tesla_get_location(self):
    #     try:
    #         r_location = requests.get(self.url_tesla_location)
    #     except Exception as e:
    #         logger.error('Connection issue with' + self.url_tesla_location + ":" + str(e))
    #         chanify.send_chanify('Connection issue with' + self.url_tesla_location + ":" + str(e))
    #         raise
    #     try:
    #         lat = float(r_location.json()['lat'])
    #         lon = float(r_location.json()['lon'])
    #         param_prox = {"lat": lat, "lon": lon}
    #     except Exception as e:
    #         logger.warning('get_location latlon= values are not valid:' + str(e))
    #         chanify.send_chanify('get_location latlon= values are not valid:' + str(e))
    #         raise
    #     try:
    #         self.db.save_location(r_location.json())
    #     except Exception as e:
    #         logger.error("Issue with saving latlon to mongodb:" + str(e))
    #         chanify.send_chanify("Issue with  saving latlon to mongodb:" + str(e))
    #     return param_prox
    #place limit on how long the air has been on

    @retry(logger=logging.Logger, delay=2, tries=3)
    def is_on_home_street(self):
        latlon = self.get_location()
        try:
            reverse_geocode_result = self.gmaps.reverse_geocode((latlon['lat'], latlon['lon']))
        except Exception as e:
            logger.warning("is_on_home_street: Issue with Gmaps geocode:" + str(e))
        try:
            for i in reverse_geocode_result:
                if 'Arcuri Court' in i['address_components'][0]['long_name']:
                    return True
            return False
        except Exception as e:
            logger.warning("is_on_home_street: output of geocode is not as expected:"+ str(e))


if __name__ == "__main__":
    obj = Tesla()
    # print(obj.is_in_service())
    # print(obj.is_battery_good()) and self.is_parked
    print(obj.get_location())

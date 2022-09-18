import json
import logging

import requests
import teslapy
from retry import retry
import googlemaps
import threading
import util.db_mongo as db_mongo
from util.logs import logger
import util.sms as sms
import custom as mababio_teslapy


class Tesla:

    def __init__(self):
REMOVED
        self.url_tesla_prox = "https://us-east4-ensure-dev-zone.cloudfunctions.net/function-tesla-prox"
        self.url_tesla_location = "https://us-east4-ensure-dev-zone.cloudfunctions.net/function-tesla-get_location"
        self.proximity_value = None
        self.url_tesla_set_temp = "https://us-east4-ensure-dev-zone.cloudfunctions.net/function-tesla-set-temp"
        self.url_tesla_info = "https://us-east4-ensure-dev-zone.cloudfunctions.net/tesla-info"
        self.db = db_mongo.DBClient()

    @retry(logger=logger, delay=0, tries=3)
    def set_temp(self, temp='22.7778'):
        param = {"temp": temp}
        return requests.post(self.url_tesla_set_temp, json=param)

    def is_battery_good(self):
        look = requests.get(self.url_tesla_info).json()
        print(look)


    # def is_tesla_ready_for_climate_on(self):
    # 1. car is not moving, and parked for a while
 #       - store gps location and add time_share timestamp if hasn't chnage then
    # 2. car is not home
    # 3. battery is good enough
    # 4. not in vacation mode - save to mongo
    # 5.  not in_service
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

    @retry(logger=logger, delay=2, tries=2)
    def get_location(self):
        try:
            # r_location = requests.get(self.url_tesla_location)
            r_location = self.tesla_get_location()
        except Exception as e:
            logger.error('Connection issue with' + self.url_tesla_location + ":" + str(e))
            sms.send_sms('Connection issue with' + self.url_tesla_location + ":" + str(e))
            raise
        try:
            lat = float(r_location['lat'])
            lon = float(r_location['lon'])
            param_prox = {"lat": lat, "lon": lon}
        except Exception as e:
            logger.warning('get_location latlon= values are not valid:' + str(e))
            sms.send_sms('get_location latlon= values are not valid:' + str(e))
            raise
        try:
            self.db.save_location(r_location)
        except Exception as e:
            logger.error("Issue with saving latlon to mongodb:" + str(e))
            sms.send_sms("Issue with  saving latlon to mongodb:" + str(e))
        return param_prox

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

    def tesla_get_location(self):
        with mababio_teslapy.Tesla('michaelkwasi@gmail.com') as tesla:
            vehicles = tesla.vehicle_list()
            vehicles[0].sync_wake_up()
            tesla_data = vehicles[0].api('VEHICLE_DATA')['response']['drive_state']
            lat = str(tesla_data['latitude'])
            lon = str(tesla_data['longitude'])
            data = {'lat': lat, 'lon': lon, 'speed':tesla_data['speed']}
            # data[] = lat
            # data['lon'] = lon
            # data['speed'] = tesla_data['speed']
            #json_data = json.dumps(data)
        #return json.loads(json_data)
        return data


if __name__ == "__main__":
    obj = Tesla()
    val =  obj.tesla_get_location()
    val_type =  type(val)
    print(val)
    print(val_type)
    print(obj.is_on_home_street())

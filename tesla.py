import requests
from retry import retry
import googlemaps


class Tesla:

    def __init__(self):
        self.hold = 1
        self.gmaps = googlemaps.Client(key='AIzaSyCpSgkND8wBAdlK8sSaqjgqFMPx7AJmq68')
        self.url_tesla_prox = "https://us-east4-ensure-dev-zone.cloudfunctions.net/function-tesla-prox"
        self.url_tesla_location = "https://us-east4-ensure-dev-zone.cloudfunctions.net/function-tesla-get_location"
        self.proximity_value = None

    # def set_temp(self,temp):
    #     return True
    #
    #
    # def is_tesla_ready_for_climate_on(self):
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

    @retry(delay=2, tries=3)
    def is_close(self):
        return_value = self.get_full_proximity()
        self.proximity_value = return_value['difference']
        if return_value['is_on_arcuri'] and return_value['is_close']:
            return True
        else:
            return False

    @retry(delay=2, tries=3)
    def get_full_proximity(self):
        r_location = requests.post(self.url_tesla_location)
        lat = float(r_location.json()['lat'])
        lon = float(r_location.json()['lon'])
        param_prox = {"lat": lat, "lon": lon}
        return requests.post(self.url_tesla_prox, json=param_prox).json()

    @retry(delay=2, tries=3)
    def get_location(self):
        r_location = requests.post(self.url_tesla_location)
        lat = float(r_location.json()['lat'])
        lon = float(r_location.json()['lon'])
        param_prox = {"lat": lat, "lon": lon}
        return param_prox

    def is_on_home_street(self):
        latlon = self.get_location()
        reverse_geocode_result = self.gmaps.reverse_geocode((latlon['lat'], latlon['lon']))
        for i in reverse_geocode_result:
            if 'Arcuri Court' in i['address_components'][0]['long_name']:
                return True
        return False

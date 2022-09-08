import requests
from retry import retry
import googlemaps
import time
import sms
import os





class TAP:

    def __init__(self):
        self.garage_still_open = None
        self.stil_on_home_street = None
        self.url_tesla_prox = "https://us-east4-ensure-dev-zone.cloudfunctions.net/function-tesla-prox"
        self.url_tesla_location = "https://us-east4-ensure-dev-zone.cloudfunctions.net/function-tesla-get_location"
REMOVED
        self.garage_open_limit = 300  # 5mins
        self.confirmation_limit = 20

    def garage_isopen(self):
        url_myq_garage = "https://us-east4-ensure-dev-zone.cloudfunctions.net/function-trigger-myq"
        param = {"isopen": ''}
        if requests.post(url_myq_garage, json=param).json()['isopen'] == 'closed':
            return False
        else:
            return True

    def confirmation_before_armed(self):
        print('in main ...2')
        while self.garage_isopen() and not self.garage_open_limit == 0:
            print('Checking if still open for 5 mins')
            time.sleep(5)
            self.garage_open_limit -= 5
        else:
            print('either is still open or checked if open for more then 5 mins OR garage is closed')
            if not self.garage_isopen() and self.is_tesla_moving() and not self.isOnHomeStreet():
                print('garage is closed and car is moving and not on home street')
                return True
            elif self.garage_isopen() and self.garage_open_limit == 0:
                print('garage has been open for more than 5 mins and we are terminating confirmation function')
                self.garage_still_open = True
                return False
            else:
                print('in main ...6')
                while self.isOnHomeStreet() and not self.confirmation_limit == 0:
                    print('car is parked on street with garage closed')
                    time.sleep(5)
                    self.confirmation_limit -= 5
                else:
                    print('in main ...8')
                    if not self.isOnHomeStreet(): # not on home street
                        print('Not sure about this case')
                        return True
                    else:
                        print('in main ...10')
                        self.stil_on_home_street = True
                        return False

    def is_tesla_moving(self):
        self.url_tesla_location = "https://us-east4-ensure-dev-zone.cloudfunctions.net/function-tesla-get_location"
        speed = requests.post(self.url_tesla_location).json()['speed']
        if speed == 'None':
            return False
        else:
            return True
    @retry(delay=2, tries=3)
    def isclose(self):
        r_location = requests.post(self.url_tesla_location)
        lat = float(r_location.json()['lat'])
        lon = float(r_location.json()['lon'])
        param_prox = {"lat": lat, "lon": lon}
        return_value = requests.post(self.url_tesla_prox, json=param_prox).json()
        if return_value['is_on_arcuri'] and return_value['is_close']:
            return True
        else:
            return False

    @retry(delay=2, tries=3)
    def get_proximity(self):
        r_location = requests.post(self.url_tesla_location)
        lat = float(r_location.json()['lat'])
        lon = float(r_location.json()['lon'])
        param_prox = {"lat": lat, "lon": lon}
        return requests.post(self.url_tesla_prox, json=param_prox).json()['difference']

    @retry(delay=2, tries=3)
    def getlocation(self):
        r_location = requests.post(self.url_tesla_location)
        lat = float(r_location.json()['lat'])
        lon = float(r_location.json()['lon'])
        param_prox = {"lat": lat, "lon": lon}
        return param_prox

    def isOnHomeStreet(self):
        latlon = self.getlocation()
        lat = latlon['lat']
        lon = latlon['lon']
        reverse_geocode_result = self.gmaps.reverse_geocode((lat, lon))
        for i in reverse_geocode_result:
            if 'Arcuri Court' in i['address_components'][0]['long_name']:
                return True
        return False

    def garage(self,state):
        url_myq_garage = "https://us-east4-ensure-dev-zone.cloudfunctions.net/function-trigger-myq"
        param = {"state": state}
        return requests.post(url_myq_garage, json=param).json()

    def trigger_tesla_home_automation(self,IFTTT_TRIGGER_LOCK):
        #garage('on')
        print('do tesla automation when home')
        IFTTT_TRIGGER_LOCK = False


    def tesla_home_automation_engine(self,IFTTT_TRIGGER_LOCK):
        proximity_value = self.get_proximity()
        while not self.isclose():
            if proximity_value < 1:
                print("Delay for 2 secs")
                time.sleep(2)
                proximity_value = self.get_proximity()
            elif proximity_value < 2:
                print("Delay for 15 sec")
                time.sleep(15)
                proximity_value = self.get_proximity()
            elif proximity_value < 3:
                print("Delay for 2 mins")
                time.sleep(120)
                proximity_value = self.get_proximity()
            elif proximity_value < 7:
                print("Delay for 5 mins")
                time.sleep(300)
                proximity_value = self.get_proximity()
            else:
                print("Delay for 15 mins")
                time.sleep(900)
                proximity_value = self.get_proximity()
        else:
            self.trigger_tesla_home_automation(IFTTT_TRIGGER_LOCK)


if __name__ == "__main__":
REMOVED
    IFTTT_TRIGGER_LOCK = False # '' #globally set GCP var

    if not IFTTT_TRIGGER_LOCK:
        IFTTT_TRIGGER_LOCK = True
        tesla = TAP()
        if tesla.confirmation_before_armed():
            sms.send_sms(number, 'trigger tesla home automation!')
            tesla.tesla_home_automation_engine(IFTTT_TRIGGER_LOCK)
        elif tesla.garage_still_open:
            sms.send_sms(number, ' Garage door has been open for 5 mins. would your like to close, leave open or are you loading the bikes??')
        elif tesla.stil_on_home_street:
            sms.send_sms(number, 'limit of 5 mins has been meet or still on Arcui ct')
    else:
        sms.send_sms(number, 'Automation has been kicked off already. Appears the garage was opened remotely')

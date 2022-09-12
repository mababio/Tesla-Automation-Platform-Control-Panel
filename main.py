import requests
from retry import retry
import googlemaps
import time
import sms
import os
from flask import Flask
from flask_executor import Executor
import pymongo
from pymongo.server_api import ServerApi

REMOVED


class TAP:

    def __init__(self):
        self.proximity_value = None
        self.garage_still_open = None
        self.stil_on_home_street = None
        self.url_tesla_prox = "https://us-east4-ensure-dev-zone.cloudfunctions.net/function-tesla-prox"
        self.url_tesla_location = "https://us-east4-ensure-dev-zone.cloudfunctions.net/function-tesla-get_location"
REMOVED
        self.garage_open_limit = 100  # 5mins
        self.confirmation_limit = 100
REMOVED
        self.collection = client['tesla']['tesla_trigger']

    def setIFTTT_TRIGGER_LOCK(self,bolval):
        myquery = {"_id": "IFTTT_TRIGGER_LOCK"}
        newvalues = {"$set": {"lock": bolval}}
        self.collection.update_one(myquery, newvalues)

    def getIFTTT_TRIGGER_LOCK(self):
        return self.collection.find_one()['lock']


    def garage_isopen(self):
        url_myq_garage = "https://us-east4-ensure-dev-zone.cloudfunctions.net/function-trigger-myq"
        param = {"isopen": ''}
        if requests.post(url_myq_garage, json=param).json()['isopen'] == 'closed':
            return False
        else:
            return True

    def confirmation_before_armed(self):
        while self.garage_isopen() and not self.garage_open_limit == 0:
            sms.send_sms( 'Checking if still open for 5 mins' + str(self.garage_open_limit))
            time.sleep(5)
            self.garage_open_limit -= 5
        else:
            if not self.garage_isopen() and self.is_tesla_moving() and not self.isOnHomeStreet():
                sms.send_sms('garage is closed and car is moving and not on home street')
                return True
            elif self.garage_isopen() and self.garage_open_limit == 0:
                sms.send_sms( 'garage has been open for more than 5 mins and we are terminating confirmation function')
                self.garage_still_open = True
                return False
            else:
                while self.isOnHomeStreet() and not self.confirmation_limit == 0:
                    sms.send_sms( 'car is parked on street with garage closed')
                    time.sleep(5)
                    self.confirmation_limit -= 5
                else:
                    if not self.isOnHomeStreet(): # not on home street
                        sms.send_sms( 'Not sure about this case, but returning true')
                        return True
                    else:
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
    def getlocation(self):
        r_location = requests.post(self.url_tesla_location)
        lat = float(r_location.json()['lat'])
        lon = float(r_location.json()['lon'])
        param_prox = {"lat": lat, "lon": lon}
        return param_prox

    def isOnHomeStreet(self):
        latlon = self.getlocation()
        reverse_geocode_result = self.gmaps.reverse_geocode((latlon['lat'], latlon['lon']))
        for i in reverse_geocode_result:
            if 'Arcuri Court' in i['address_components'][0]['long_name']:
                return True
        return False

    def garage(self, state):
        url_myq_garage = "https://us-east4-ensure-dev-zone.cloudfunctions.net/function-trigger-myq"
        param = {"state": state}
        return requests.post(url_myq_garage, json=param).json()

    def trigger_tesla_home_automation(self):
        self.garage('open')
        sms.send_sms( 'Garage door opening!')
        
    def cleanup(self):
        sms.send_sms( 'cleaning up')
        time.sleep(5)
        self.setIFTTT_TRIGGER_LOCK("False")
        
    def tesla_home_automation_engine(self):

        while not self.isclose():
            if self.proximity_value < .07:
                continue
            elif self.proximity_value < 1:
                sms.send_sms("Delay for 1 secs")
                time.sleep(1)
            elif self.proximity_value < 2:
                sms.send_sms("Delay for 15 sec")
                time.sleep(15)
            elif self.proximity_value < 3:
                sms.send_sms("Delay for 2 mins")
                time.sleep(120)
            elif self.proximity_value < 7:
                sms.send_sms("Delay for 5 mins")
                time.sleep(300)
            else:
                sms.send_sms("Delay for 15 mins")
                time.sleep(900)
        else:
            self.trigger_tesla_home_automation()


app = Flask(__name__)
executor = Executor(app)


@app.route("/")
def kickOffJobBG():
    executor.submit(tesla_automation)
    return 'Scheduled a job'


def tesla_automation():
    tesla = TAP()
    IFTTT_TRIGGER_LOCK = tesla.getIFTTT_TRIGGER_LOCK()

    if IFTTT_TRIGGER_LOCK == 'False':
        tesla.setIFTTT_TRIGGER_LOCK("True")
        if tesla.confirmation_before_armed():
            sms.send_sms('trigger tesla home automation!')
            tesla.tesla_home_automation_engine()
            sms.send_sms('automation Done')
            tesla.cleanup()
        elif tesla.garage_still_open:
            sms.send_sms(' Garage door has been open for 5 mins. would your like to close, '
                                 'leave open or are you'
                                 ' loading the bikes??')
            sms.send_sms( 'automation Done')
            tesla.cleanup()
        elif tesla.stil_on_home_street:
            sms.send_sms('limit of 5 mins has been meet or still on Arcui ct')
            sms.send_sms('automation Done')
            tesla.cleanup()
    else:
        sms.send_sms('Automation has been kicked off already. Appears the garage was opened remotely')


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

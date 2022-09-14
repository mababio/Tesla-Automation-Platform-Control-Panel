import requests

import googlemaps
import time
import sms
import os
from flask import Flask
from flask import g
from flask_executor import Executor
from db_mongo import db_client
from tesla import Tesla

class TAP:

    def __init__(self):
        self.proximity_value = None
        self.garage_still_open = None
        self.stil_on_home_street = None
        self.url_tesla_prox = "https://us-east4-ensure-dev-zone.cloudfunctions.net/function-tesla-prox"
        self.url_tesla_location = "https://us-east4-ensure-dev-zone.cloudfunctions.net/function-tesla-get_location"
REMOVED
        self.garage_open_limit = 20  # 5mins
        self.confirmation_limit = 20
        self.db = db_client()
        self.tesla = Tesla()

    def garage_isopen(self):
        url_myq_garage = "https://us-east4-ensure-dev-zone.cloudfunctions.net/function-trigger-myq"
        param = {"isopen": ''}
        if requests.post(url_myq_garage, json=param).json()['isopen'] == 'closed':
            return False
        else:
            return True

    def confirmation_before_armed(self):
        while self.garage_isopen() and not self.garage_open_limit == 0:
            sms.send_sms('Checking if still open for 5 mins' + str(self.garage_open_limit))
            time.sleep(5)
            self.garage_open_limit -= 5
        else:
            if not self.garage_isopen() and self.tesla.is_tesla_moving() and not self.tesla.is_on_home_street():
                sms.send_sms('garage is closed and car is moving and not on home street')
                return True
            elif self.garage_isopen() and self.garage_open_limit == 0:
                sms.send_sms('garage has been open for more than 5 mins and we are terminating confirmation function')
                self.garage_still_open = True
                return False
            else:
                while self.tesla.is_on_home_street() and not self.confirmation_limit == 0:
                    sms.send_sms('car is parked on street with garage closed')
                    time.sleep(5)
                    self.confirmation_limit -= 5
                else:
                    if not self.tesla.is_on_home_street():  # not on home street
                        sms.send_sms('Not sure about this case, but returning true')
                        return True
                    else:
                        self.stil_on_home_street = True
                        return False



    def garage(self, state):
        url_myq_garage = "https://us-east4-ensure-dev-zone.cloudfunctions.net/function-trigger-myq"
        param = {"state": state}
        return requests.post(url_myq_garage, json=param).json()

    def trigger_tesla_home_automation(self):
        self.garage('open')
        sms.send_sms('Garage door opening!')

    def cleanup(self):
        sms.send_sms('Setinng job done')
        self.db.set_door_close_status("came_home")

    def tesla_home_automation_engine(self):
        while not self.telsa.is_close():
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


@app.before_request
def before_request():
    g.db = db_client()


@app.route("/open")
def kick_off_job_ifttt_open_bg():
    if g.db.get_tesla_database()['tesla_trigger'].find_one()['lock'] == 'False':
        myquery = {"_id": "IFTTT_TRIGGER_LOCK"}
        newvalues = {"$set": {"lock": "True"}}
        g.db.get_tesla_database()['tesla_trigger'].update_one(myquery, newvalues)
        executor.submit(tesla_automation)
        return 'Scheduled a job'
    else:
        sms.send_sms("Process is already running")
        return 'Process is already running'


@app.route("/close")
def kick_off_job_ifttt_close_bg():
    if g.db.get_door_close_status() == 'came_home':
        executor.submit(garage_door_closed)
        sms.send_sms('Car has arrive and door was closed')
        return 'Car has arrive and door was closed'
    else:
        sms.send_sms('Door was not closed b/c car came home')
        return 'Door was not closed b/c car came home'


def garage_door_closed():
    myquery_ifttt_trigger_lock = {"_id": "IFTTT_TRIGGER_LOCK"}
    ct = {"$set": {"lock": "False"}}
    myquery_garage_closed_reason = {"_id": "garage"}
    newvalues_ifttt_trigger_lock = {"$set": {"locked_reason": " "}}

    g.db.get_tesla_database()['tesla_trigger'].update_one(myquery_ifttt_trigger_lock, ct)
    g.db.get_tesla_database()['garage'].update_one(myquery_garage_closed_reason, newvalues_ifttt_trigger_lock)


def tesla_automation():
    sms.send_sms('before!')
    tesla_tap = TAP()
    sms.send_sms('after!')
    if tesla_tap.confirmation_before_armed():
        sms.send_sms('trigger tesla home automation!')
        tesla_tap.tesla_home_automation_engine()
        sms.send_sms('automation Done')
    elif tesla_tap.garage_still_open:
        sms.send_sms(' Garage door has been open for 5 mins. would your like to close, '
                     'leave open or are you'
                     ' loading the bikes??')
        sms.send_sms('automation Done')
    elif tesla_tap.stil_on_home_street:
        sms.send_sms('limit of 5 mins has been meet or still on Arcui ct')
        sms.send_sms('automation Done')
    tesla_tap.cleanup()


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

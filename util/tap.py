import requests
import time

from retry import retry

import util.db_mongo as db_mongo
import util.sms as sms
import util.tesla as tesla
from util.logs import logger


class TAP:

    def __init__(self):
        self.garage_still_open = None
        self.stil_on_home_street = None
        self.garage_open_limit = 20  # 5mins
        self.confirmation_limit = 20
        self.db = db_mongo.DBClient()
        self.tesla_obj = tesla.Tesla()

    def garage_isopen(self):
        url_myq_garage = "https://us-east4-ensure-dev-zone.cloudfunctions.net/function-trigger-myq"
        param = {"isopen": ''}
        if requests.post(url_myq_garage, json=param).json()['isopen'] == 'closed':
            return False
        else:
            return True

    def confirmation_before_armed(self):
        while self.garage_isopen() and not self.garage_open_limit == 0:
            sms.send_push_notification('Checking if still open for 5 mins' + str(self.garage_open_limit))
            time.sleep(5)
            self.garage_open_limit -= 5
        else:
            if not self.garage_isopen() and self.tesla_obj.is_tesla_moving() and not self.tesla_obj.is_on_home_street():
                sms.send_push_notification('garage is closed and car is moving and not on home street')
                return True
            elif self.garage_isopen() and self.garage_open_limit == 0:
                sms.send_push_notification('garage has been open for more than 5 mins and we are terminating confirmation function')
                self.garage_still_open = True
                return False
            else:
                while self.tesla_obj.is_on_home_street() and not self.confirmation_limit == 0:
                    sms.send_push_notification('car is parked on street with garage closed')
                    time.sleep(5)
                    self.confirmation_limit -= 5
                else:
                    if not self.tesla_obj.is_on_home_street():  # not on home street
                        sms.send_push_notification('Not sure about this case, but returning true')
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
        sms.send_push_notification('Garage door opening!')

    def cleanup(self):
        sms.send_push_notification('Setinng job done')
        self.db.set_door_close_status("came_home")

    @retry(logger=logger, delay=300, tries=3)
    def tesla_home_automation_engine(self):
        try:
            while not self.tesla_obj.is_close():
                if self.tesla_obj.proximity_value < .07:
                    continue
                elif self.tesla_obj.proximity_value < 1:
                    sms.send_push_notification("Delay for 1 secs")
                    time.sleep(1)
                elif self.tesla_obj.proximity_value < 2:
                    sms.send_push_notification("Delay for 15 sec")
                    time.sleep(15)
                elif self.tesla_obj.proximity_value < 3:
                    sms.send_push_notification("Delay for 2 mins")
                    time.sleep(120)
                elif self.tesla_obj.proximity_value < 7:
                    sms.send_push_notification("Delay for 5 mins")
                    time.sleep(300)
                else:
                    sms.send_push_notification("Delay for 15 mins")
                    time.sleep(900)
            else:
                self.trigger_tesla_home_automation()
        except Exception as e:
            sms.send_push_notification('tesla_home_automation_engine: Issue found in the while loop')
            logger.error('tesla_home_automation_engine: Issue found in the while loop')
            raise


if __name__ == "__main__":
    obj = TAP()
    print(obj.tesla_obj.is_close())
    #print(obj.tesla_obj.proximity_value)
    #sms.send_push_notification("Delay for 1 secsss")
    #time.sleep(1)



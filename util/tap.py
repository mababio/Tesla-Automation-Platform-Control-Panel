import requests
import time

from retry import retry

import util.db_mongo as db_mongo
import util.notification as notification
import util.tesla as tesla
from util.logs import logger
from config import settings


class TAP:

    def __init__(self):
        self.garage_still_open = None
        self.still_on_home_street = None
        self.garage_open_limit = settings['production']['garage_open_limit']
        self.confirmation_limit = settings['production']['confirmation_limit']
        self.db = db_mongo.DBClient()
        self.tesla_obj = tesla.Tesla()
        self.url_myq_garage = settings['production']['URL']['myq_garage']

    def garage_isopen(self):
        param = {"isopen": ''}
        if requests.post(self.url_myq_garage, json=param).json()['isopen'] == 'closed':
            return False
        else:
            return True

    def confirmation_before_armed(self):
        while self.garage_isopen() and not self.garage_open_limit == 0:
            notification.send_push_notification('Checking if still open for 5 mins' + str(self.garage_open_limit))
            time.sleep(5)
            self.garage_open_limit -= 5
        else:
            if not self.garage_isopen() and self.tesla_obj.is_tesla_moving() and not self.tesla_obj.is_on_home_street():
                notification.send_push_notification('garage is closed and car is moving and not on home street')
                return True
            elif self.garage_isopen() and self.garage_open_limit == 0:
                notification.send_push_notification('garage has been open for more than 5 mins and we are terminating '
                                                    'confirmation function')
                self.garage_still_open = True
                return False
            else:
                while self.tesla_obj.is_on_home_street() and not self.confirmation_limit == 0:
                    notification.send_push_notification('car is parked on street with garage closed')
                    time.sleep(5)
                    self.confirmation_limit -= 5
                else:
                    if not self.tesla_obj.is_on_home_street():  # not on home street
                        notification.send_push_notification('Not sure about this case, but returning true')
                        return True
                    else:
                        self.still_on_home_street = True
                        return False

    def garage(self, state):
        param = {"state": state}
        return requests.post(settings['production']['URL']['myq_garage'], json=param).json()

    def trigger_tesla_home_automation(self):
        self.garage('open')
        notification.send_push_notification('Garage door opening!')

    def cleanup(self):
        notification.send_push_notification('Setinng job done')
        self.db.set_door_close_status("came_home")

    @retry(logger=logger, delay=300, tries=3)
    def tesla_home_automation_engine(self):
        try:
            while not self.tesla_obj.is_close():
                if self.tesla_obj.proximity_value < .07:
                    continue
                elif self.tesla_obj.proximity_value < 1:
                    notification.send_push_notification("Delay for 1 secs")
                    time.sleep(1)
                elif self.tesla_obj.proximity_value < 2:
                    notification.send_push_notification("Delay for 15 sec")
                    time.sleep(15)
                elif self.tesla_obj.proximity_value < 3:
                    notification.send_push_notification("Delay for 2 mins")
                    time.sleep(120)
                elif self.tesla_obj.proximity_value < 7:
                    notification.send_push_notification("Delay for 5 mins")
                    time.sleep(300)
                elif self.tesla_obj.proximity_value < 10:
                    notification.send_push_notification("Delay for 10 mins")
                    time.sleep(600)
                else:
                    notification.send_push_notification("Delay for 15 mins")
                    time.sleep(900)
            else:
                self.trigger_tesla_home_automation()
        except Exception as e:
            notification.send_push_notification('tesla_home_automation_engine: Issue found in the while loop ' + str(e))
            logger.error('tesla_home_automation_engine: Issue found in the while loop ' + str(e))
            raise


if __name__ == "__main__":
    obj = TAP()
    print(obj.tesla_obj.is_close())
    #print(obj.tesla_obj.proximity_value)
    #notification.send_push_notification("Delay for 1 secsss")
    #time.sleep(1)



import time
from retry import retry
import util.db_mongo as db_mongo
import util.notification as notification
import util.tesla as tesla
from util.logs import logger
from config import settings
import util.garage as garage




class TAP:

    def __init__(self):
        self.garage_still_open = None
        self.still_on_home_street = None
        self.garage_open_limit = settings['production']['garage_open_limit']
        self.confirmation_limit = settings['production']['confirmation_limit']
        self.db = db_mongo.DBClient()
        self.tesla_obj = tesla.Tesla()

    def confirmation_before_armed(self):
        while garage.garage_is_open() and not self.garage_open_limit == 0:
            notification.send_push_notification('Garage is open ' + str(self.garage_open_limit) +
                                                ' seconds remaining to confirm closure')
            time.sleep(5)
            self.garage_open_limit -= 5
        else:
            while self.tesla_obj.is_on_home_street() and not self.confirmation_limit == 0:
                notification.send_push_notification('Waiting ' + str(self.confirmation_limit) +
                                                    'seconds for conditions to be met for trigger')
                time.sleep(5)
                self.confirmation_limit -= 5
            else:
                if not garage.garage_is_open() and not self.tesla_obj.is_on_home_street():
                    garage.set_close_reason(garage.GarageCloseReason.DRIVE_AWAY, self.db)
                    return True
                else:
                    return False

    def trigger_tesla_home_automation(self):
        garage.open_garage(self.db)
        notification.send_push_notification('Garage door opening!')
        logger.info('trigger_tesla_home_automation::::: Garage door was triggered to open')

    def cleanup(self):
        notification.send_push_notification('Setinng job done')

    @retry(logger=logger, delay=300, tries=3)
    def tesla_home_automation_engine(self):
        try:
            while not self.tesla_obj.is_close():
                if self.tesla_obj.proximity_value < .07:
                    continue
                elif self.tesla_obj.proximity_value < .3:
                    notification.send_push_notification("Delay for 1 secs")
                    time.sleep(1)
                elif self.tesla_obj.proximity_value < 1:
                    notification.send_push_notification("Delay for 15 sec")
                    time.sleep(10)
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
    print(obj.garage_is_open())
    # print(obj.tesla_obj.is_close())

    # obj.tesla_obj.get_location()
    # while True:
    #     obj.tesla_obj.get_location()
    #     time.sleep(2)

    #print(obj.tesla_obj.proximity_value)
    #notification.send_push_notification("Delay for 1 secsss")
    #time.sleep(1)



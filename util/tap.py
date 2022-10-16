import time
import util.db_mongo as db_mongo
import util.notification as notification
import util.tesla as tesla
from util.logs import logger
from config import settings
import util.garage as garage
from util import gcp_scheduler as scheduler


class TAP:

    def __init__(self):
        self.garage_still_open = None
        self.still_on_home_street = None
        self.garage_open_limit = settings['production']['garage_open_limit']
        self.confirmation_limit = settings['production']['confirmation_limit']
        self.db = db_mongo.DBClient()
        self.tesla_obj = tesla.Tesla()
        self.safety = True

    def confirmation_before_armed(self):
        while garage.garage_is_open() and not self.garage_open_limit == 0:
            notification.send_push_notification('Garage is open for {} seconds remaining to confirm closure'
                                                .format(str(self.garage_open_limit)))
            time.sleep(5)
            self.garage_open_limit -= 5
        else:
            while self.tesla_obj.is_on_home_street() and not self.confirmation_limit == 0:
                notification.send_push_notification('Waiting {} seconds for conditions to be met for trigger'
                                                    .format(str(self.confirmation_limit)))
                time.sleep(5)
                self.confirmation_limit -= 5
            else:
                if not garage.garage_is_open() and not self.tesla_obj.is_on_home_street():
                    return True
                else:
                    return False

    def trigger_tesla_home_automation(self):
        self.db.publish_open_garage()
        self.db.set_door_open_status(garage.GarageOpenReason.DRIVE_HOME)
        notification.send_push_notification('Garage door opening!')
        logger.info('trigger_tesla_home_automation::::: Garage door was triggered to open')
        job = scheduler.pause_job(scheduler.schedule_Jobs.TESLA_LONG_TERM)
        if job:
            notification.send_push_notification('job has been disabled!')
        else:
            logger.error("Cloud Scheduler job has trouble disabling job. DISABLE NOW!!!!")
            notification.send_push_notification("Cloud Scheduler job has trouble disabling job. DISABLE NOW!!!!")
        return True

    def cleanup(self):
        notification.send_push_notification('Closing out Run')

    def tesla_home_automation_engine(self):
        try:
            while not self.tesla_obj.is_near() and self.safety:
                if self.tesla_obj.proximity_value < .07:
                    notification.send_push_notification("Delay for 1 secs close by")
                    time.sleep(1)
                elif self.tesla_obj.proximity_value < .3:
                    notification.send_push_notification("Delay for 1 secs")
                    time.sleep(1)
                elif self.tesla_obj.proximity_value < 1:
                    notification.send_push_notification("Delay for 15 sec")
                    time.sleep(15)
                elif self.tesla_obj.proximity_value < 3:
                    scheduler.schedule_proximity_job(2, self.db)
                    break
                elif self.tesla_obj.proximity_value < 7:
                    scheduler.schedule_proximity_job(5, self.db)
                    break
                elif self.tesla_obj.proximity_value < 10:
                    scheduler.schedule_proximity_job(10, self.db)
                    break
                else:
                    scheduler.schedule_proximity_job(15, self.db)
                    break
            else:
                self.safety = False  # To prevent the while from accidentally running again
                self.trigger_tesla_home_automation()
                return True
        except Exception as e:
            notification.send_push_notification('tesla_home_automation_engine:::::: Issue found in the while loop '
                                                + str(e))
            logger.error('tesla_home_automation_engine:::::: Issue found in the while loop ' + str(e))
            raise


if __name__ == "__main__":
    obj = TAP()
    print(garage.garage_is_open())
    # print(obj.tesla_obj.is_close())

    # obj.tesla_obj.get_location()
    # while True:
    #     obj.tesla_obj.get_location()
    #     time.sleep(2)

    # print(obj.tesla_obj.proximity_value)
    # notification.send_push_notification("Delay for 1 secsss")
    # time.sleep(1)

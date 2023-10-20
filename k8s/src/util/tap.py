import time
import requests
import sys
from config import settings
sys.path.append('../')
import tesla, garage, notification, gcp_scheduler
from logs import logger
import utils


class TAP:

    def __init__(self):
        self.tesla_data_services_url = "tesla_data_services:8000"
        self.garage_still_open = None
        self.still_on_home_street = None
        self.garage_open_limit = settings['production']['garage_open_limit']
        self.confirmation_limit = settings['production']['confirmation_limit']
        self.tesla_obj = tesla.Tesla()
        self.safety = True
        self.sess = requests.Session()
        adapter = requests.adapters.HTTPAdapter(max_retries=20)
        self.sess.mount('https://', adapter)
        self.url_tesla_data_services = settings['production']['URL']['tesla_data_services'] + '/api/car'

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
        # self.db.publish_open_garage()
        garage.request_open()
        self.sess.put('{}{}{}'.format(self.url_tesla_data_services, '/update/door_opened/',
                                      garage.GarageOpenReason.DRIVE_HOME))
        # set_door_open_status(garage.GarageOpenReason.DRIVE_HOME)
        notification.send_push_notification('Garage door opening!')
        logger.info('trigger_tesla_home_automation::::: Garage door was triggered to open')
        job = gcp_scheduler.pause_job(gcp_scheduler.schedule_Jobs.TESLA_LONG_TERM)
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
                if self.tesla_obj.proximity_value < .019:
                    notification.send_push_notification("Delay for 2 secs close by")
                    time.sleep(2)
                if self.tesla_obj.proximity_value < .3:
                    notification.send_push_notification("Delay for 2 secs")
                    time.sleep(4)
                elif self.tesla_obj.proximity_value < 1:
                    notification.send_push_notification("Delay for 15 sec")
                    time.sleep(15)
                elif self.tesla_obj.proximity_value < 3:
                    gcp_scheduler.schedule_proximity_job(2)
                    break
                elif self.tesla_obj.proximity_value < 7:
                    gcp_scheduler.schedule_proximity_job(5)
                    break
                elif self.tesla_obj.proximity_value < 10:
                    gcp_scheduler.schedule_proximity_job(10)
                    break
                elif self.tesla_obj.proximity_value < 12:
                    gcp_scheduler.schedule_proximity_job(15)
                    break
                else:
                    gcp_scheduler.schedule_proximity_job(25)
                    break
            else:
                self.safety = False  # To prevent the while from accidentally running again
                self.trigger_tesla_home_automation()
                return True
        except Exception as e:
            notification.send_push_notification('tesla_home_automation_engine:::::: Issue found in the while loop '
                                                + str(e))
            logger.error('tesla_home_automation_engine:::::: Issue found in the while loop ' + str(e))
            utils.set_car_document('trigger', False)
            raise


if __name__ == "__main__":
    obj = TAP()
    print(obj.tesla_home_automation_engine())
    # print(obj.tesla_obj.is_close())

    # obj.tesla_obj.get_location()
    # while True:
    #     obj.tesla_obj.get_location()
    #     time.sleep(2)

    # print(obj.tesla_obj.proximity_value)
    # notification.send_push_notification("Delay for 1 secsss")
    # time.sleep(1)

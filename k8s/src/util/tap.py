import os
import time

import requests

import garage
import notification
import tesla
import utils
from logs import logger


class TAP:

    def __init__(self):
        try:
            self.garage_open_limit = int(os.environ["GARAGE_OPEN_LIMIT"])
            self.confirmation_limit = int(os.environ["CONFIRMATION_LIMIT"])
            self.tesla_data_services_url = f'{os.environ["TESLA_DATA_SERVICES_BASE_URL"]}/api/car'
        except KeyError:
            logger.error('tap.py::::: Environment variable not set')
            raise
        self.garage_still_open = None
        self.still_on_home_street = None
        self.tesla_obj = tesla.Tesla()
        self.safety = True
        self.sess = requests.Session()

    def confirmation_before_armed(self):
        """
        Check if garage is open and car is on home street. If so, send a notification to confirm
        :return:
        """
        while garage.garage_is_open() and self.garage_open_limit != 0:
            notification.send_push_notification(f'Garage is open for {str(self.garage_open_limit)} '
                                                f'seconds remaining to confirm closure')
            time.sleep(5)
            self.garage_open_limit -= 5
        while self.tesla_obj.is_on_home_street() and self.confirmation_limit != 0:
            notification.send_push_notification(f'Waiting {str(self.confirmation_limit)}'
                                                f' seconds for conditions '
                                                f'to be met for trigger')
            time.sleep(5)
            self.confirmation_limit -= 5
        if not garage.garage_is_open() and not self.tesla_obj.is_on_home_street():
            return True
        return False

    def trigger_tesla_home_automation(self):
        """
        Trigger the tesla home automation when vehicle is near. Right now it's just opening the Garage door
        :return:
        """
        garage.request_open()
        self.sess.put(f'{self.tesla_data_services_url}/update/door_opened/DRIVE_HOME')
        notification.send_push_notification('Garage door opening!')
        logger.info('trigger_tesla_home_automation::::: Garage door was triggered to open')
        return True

    def cleanup(self):
        notification.send_push_notification('Closing out Run')

    def tesla_home_automation_engine(self):
        """
        Main function that runs the automation. it will run until the car is near or the garage is closed.
        :return:
        """
        try:
            while not self.tesla_obj.is_near() and self.safety:
                if self.tesla_obj.proximity_value < .019:
                    notification.send_push_notification("Delay for 2 secs close by")
                    time.sleep(2)
                if self.tesla_obj.proximity_value < .3:
                    notification.send_push_notification("Delay for 4 secs")
                    time.sleep(4)
                elif self.tesla_obj.proximity_value < 1:
                    notification.send_push_notification("Delay for 15 sec")
                    time.sleep(15)
                elif self.tesla_obj.proximity_value < 3:
                    utils.schedule_proximity_task(2)
                    break
                elif self.tesla_obj.proximity_value < 7:
                    utils.schedule_proximity_task(5)
                    break
                elif self.tesla_obj.proximity_value < 10:
                    utils.schedule_proximity_task(10)
                    break
                elif self.tesla_obj.proximity_value < 12:
                    utils.schedule_proximity_task(15)
                    break
                else:
                    utils.schedule_proximity_task(25)
                    break
            self.safety = False  # To prevent the while from accidentally running again
            self.trigger_tesla_home_automation()
            return True
        except Exception as e:
            notification.send_push_notification('tesla_home_automation_engine:::::: Issue found in the while loop '
                                                + str(e))
            logger.error('tesla_home_automation_engine:::::: Issue found in the while loop %s', str(e))
            utils.set_car_document('trigger', False)
            raise


if __name__ == "__main__":
    obj = TAP()
    print(f"value returned:::: {obj.sess.put(f'{obj.tesla_data_services_url}/update/door_opened/DRIVE_HOME')}")

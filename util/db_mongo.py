import json
import pymongo
from pymongo.server_api import ServerApi
from util import notification, garage, tesla
from util.logs import logger
from google.cloud import pubsub_v1
from config import settings


# TODO: I don't think this db client object is centralized. check and if not make it centralized

# TODO: Check if mongodb is was and is still the best option
class DBClient:

    def __init__(self):
        self.publisher = pubsub_v1.PublisherClient()
        self.tesla_obj = tesla.Tesla()
        self.tesla_gps_save_mongodb_topic = self.publisher.topic_path(settings['production']['pub_sub']
                                                                      ['gps']['project'],
                                                                      settings['production']['pub_sub']['gps']['topic'])
        self.tesla_validate_and_cleanup_topic = self.publisher.topic_path(settings['production']['pub_sub']
                                                                          ['validate_cleanup']['project'],
                                                                          settings['production']['pub_sub']
                                                                          ['validate_cleanup']['topic'])
        try:
            client = pymongo.MongoClient(settings['production']['database']['mongo']['mongo_client_url']
                                         , username=settings['production']['database']['mongo']['username'],
                                         password=settings['production']['database']['mongo']['password'],
                                         server_api=ServerApi('1'))
            self.tesla_database = client['tesla']
        except Exception as e:
            logger.error("DBClient__init__::::: Issue with connecting to Mongodb: " + str(e))
            raise

    def get_tesla_database(self):
        try:
            return self.tesla_database
        except Exception as e:
            logger.error("get_tesla_database::::: Error getting mongodb client conn to DB " + str(e))

    def get_tesla_location_is_home_value(self):
        logger.debug('get_tesla_location_is_home_value::::: Getting is_home value')
        return self.tesla_database['tesla_location'].find_one({"_id": "current"})['is_home']

    def set_tesla_location_is_home_value(self, bol_value):
        myquery = {"_id": "current"}
        new_values = {"$set": {"is_home": bol_value}}
        self.tesla_database['tesla_location'].update_one(myquery, new_values)
        logger.debug(
            'set_tesla_location_is_home_value::::: this was trigger most likely b/c we have reached home' + str(
                bol_value))

    def set_ifttt_trigger_lock(self, bol_val):
        myquery = {"_id": "IFTTT_TRIGGER_LOCK"}
        new_values = {"$set": {"lock": bol_val}}
        self.tesla_database['tesla_trigger'].update_one(myquery, new_values)
        logger.debug('set_ifttt_trigger_lock::::: Updating ifttt_trigger_lock value to' + str(bol_val))

    def set_door_close_status(self, reason):
        if isinstance(reason, garage.GarageCloseReason):
            myquery = {"_id": "garage"}
            new_values = {"$set": {"closed_reason": reason.value}}
            self.tesla_database['garage'].update_one(myquery, new_values)
            logger.debug('set_door_close_status::::: Updating door_close_status value to' + str(reason))
        else:
            logger.error('set_door_close_status::::: Issue with input given')
            raise TypeError('set_door_close_status::::: GarageCloseReason Enum type was not provided')

    def set_door_open_status(self, reason):
        if isinstance(reason, garage.GarageOpenReason):
            myquery = {"_id": "garage"}
            new_values = {"$set": {"opened_reason": reason.value}}
            self.tesla_database['garage'].update_one(myquery, new_values)
            logger.debug('set_door_open_status::::: Updating door_open_status value to' + str(reason))
        else:
            logger.error('set_door_open_status::::: Issue with input given')
            raise TypeError('set_door_open_status::::: GarageOpenReason Enum type was not provided')

    def get_ifttt_trigger_lock(self):
        logger.debug('get_ifttt_trigger_lock::::: Getting ifttt_trigger_lock value')
        return self.tesla_database['tesla_trigger'].find_one()['lock']

    def get_door_close_status(self):
        logger.debug('get_door_close_status::::: get_door_close_status: Getting door_close_status value')
        return self.tesla_database['garage'].find_one()['closed_reason']

    def get_door_open_status(self):
        logger.debug('get_door_open_status::::: get_door_open_status: Getting door_open_status value')
        return self.tesla_database['garage'].find_one({'_id': 'garage'})['opened_reason']

    def get_saved_location(self):
        return self.tesla_database['tesla_location'].find_one({'_id': 'current'})

    def save_location(self, json_lat_lon):
        if isinstance(json_lat_lon, dict):
            data_str = json.dumps(json_lat_lon)
        else:
            logger.error("save_location::::: Type dict was not provided")
            raise TypeError("save_location::::: Type dict was not provided")
        future = self.publisher.publish(self.tesla_gps_save_mongodb_topic, data_str.encode("utf-8"))
        logger.info('save_location::::: sent latlon to pubsub')
        return future

    def validate_state_then_cleanup(self):
        if not self.tesla_obj.is_near() and (self.get_door_open_status() == 'DRIVE_HOME' or
                                             self.get_door_close_status() == 'DRIVE_HOME'):
            self.set_door_open_status(garage.GarageOpenReason.DRIVE_AWAY)
            self.set_door_close_status(garage.GarageCloseReason.DRIVE_AWAY)
            self.set_ifttt_trigger_lock("False")
        elif self.tesla_obj.is_near() and (self.get_door_open_status() == 'DRIVE_AWAY' or
                                           self.get_door_close_status() == 'DRIVE_AWAY'):
            self.set_door_open_status(garage.GarageOpenReason.DRIVE_HOME)
            self.set_door_close_status(garage.GarageCloseReason.DRIVE_HOME)
            self.set_ifttt_trigger_lock("False")

    def is_climate_turned_on_via_automation(self):
        climate_state = self.tesla_database['tesla_climate_status'].find_one({'_id': 'enum'})['climate_state']
        return True if climate_state == 'climate_automation' else False

    def climate_turned_on_via_automation_before(self):
        climate_turned_on_before = self.tesla_database['tesla_climate_status'].find_one({'_id': 'enum'})[
            'climate_turned_on_before']
        return True if climate_turned_on_before == 'True' else False

    def reset_climate_automation(self):
        self.tesla_database['tesla_climate_status'].update_one({"_id": "enum"},
                                                               {"$set": {"climate_state": 'at_user_well'}})
        self.tesla_database['tesla_climate_status'].update_one({"_id": "enum"},
                                                               {"$set": {"climate_turned_on_before": 'False'}})

    def reset_all_flags_tap_is_complete(self):
        self.set_ifttt_trigger_lock('False')
        self.reset_climate_automation()
        self.set_door_close_status(garage.GarageCloseReason.DRIVE_HOME)
        if self.get_door_open_status() != garage.GarageOpenReason.DRIVE_HOME.value:
            notification.send_push_notification('door open flag was not set correctly. it has been now')
            self.set_door_open_status(garage.GarageOpenReason.DRIVE_HOME)

    def tap_set_flags_on(self):
        if self.get_ifttt_trigger_lock() != "True":
            self.set_ifttt_trigger_lock("True")
        self.set_door_open_status(garage.GarageOpenReason.DRIVE_AWAY)
        self.set_door_close_status(garage.GarageCloseReason.DRIVE_AWAY)
        self.set_tesla_location_is_home_value(False)
        self.reset_climate_automation()


if __name__ == "__main__":
    obj = DBClient()
    obj.reset_all_flags_tap_is_complete()

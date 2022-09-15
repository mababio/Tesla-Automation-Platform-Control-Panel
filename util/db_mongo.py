from datetime import datetime
import pymongo
from pymongo.server_api import ServerApi
from util.logs import logger


class DBClient:

    def __init__(self):
        try:
REMOVED
            self.tesla_database = client['tesla']
        except Exception as e:
            logger.error("Issue with connecting to Mongodb: " + str(e))
            raise

    def get_tesla_database(self):
        return self.tesla_database

    def set_ifttt_trigger_lock(self,bolval):
        myquery = {"_id": "IFTTT_TRIGGER_LOCK"}
        newvalues = {"$set": {"lock": bolval}}
        self.tesla_database['tesla_trigger'].update_one(myquery, newvalues)
        logger.debug('set_ifttt_trigger_lock: Updating ifttt_trigger_lock value to' + str(bolval))

    def set_door_close_status(self, reason):
        myquery = {"_id": "garage"}
        newvalues = {"$set": {"closed_reason": reason}}
        self.tesla_database['garage'].update_one(myquery, newvalues)
        logger.debug('set_door_close_status: Updating door_close_status value to' + str(reason))

    def get_ifttt_trigger_lock(self):
        logger.debug('get_ifttt_trigger_lock: Getting ifttt_trigger_lock value')
        return self.tesla_database['tesla_trigger'].find_one()['lock']

    def get_door_close_status(self):
        logger.debug('get_door_close_status: Getting door_close_status value')
        return self.tesla_database['garage'].find_one()['closed_reason']

    def __get_saved_location(self):
        return self.tesla_database['tesla_location'].find_one()

    def save_location(self, lat, lon):
        return_saved_location = self.__get_saved_location()
        lat_current_saved = return_saved_location['lat']
        lon_current_saved = return_saved_location['lon']
        if lat != lat_current_saved and lon != lon_current_saved:
            myquery = {"_id": 'current'}
            new_values = {"$set": {"lat": lat, "lon": lon, "timestamp": str(datetime.now())}}
            self.tesla_database['tesla_location'].update_one(myquery, new_values)
            logger.info('save_location: updating latlong to dbmongo ')
        else:
            logger.info('save_location: Current lat lon values are the same as dbmongo values')






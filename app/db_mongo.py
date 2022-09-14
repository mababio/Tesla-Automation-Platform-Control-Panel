import pymongo
from pymongo.server_api import ServerApi
# import asyncio
import time


class db_client:

    def __init__(self):
REMOVED
        self.tesla_database = client['tesla']

    def get_tesla_database(self):
        return self.tesla_database

    def set_ifttt_trigger_lock(self,bolval):
        myquery = {"_id": "IFTTT_TRIGGER_LOCK"}
        newvalues = {"$set": {"lock": bolval}}
        self.tesla_database['tesla_trigger'].update_one(myquery, newvalues)

    def set_door_close_status(self, reason):
        myquery = {"_id": "garage"}
        newvalues = {"$set": {"closed_reason": reason}}
        self.tesla_database['garage'].update_one(myquery, newvalues)

    def get_ifttt_trigger_lock(self):
        return self.tesla_database['tesla_trigger'].find_one()['lock']

    def get_door_close_status(self):
        return self.tesla_database['garage'].find_one()['closed_reason']

    def save_location(self,lat,lon):
        time.sleep(20)
        print('done!!!')
        # save latlong to mongodb





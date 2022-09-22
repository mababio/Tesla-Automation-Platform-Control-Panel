import json
import pymongo
from pymongo.server_api import ServerApi
from util.logs import logger
from google.cloud import pubsub_v1


class DBClient:

    def __init__(self):
        self.publisher = pubsub_v1.PublisherClient()
        self.tesla_gps_save_mongodb_topic = self.publisher.topic_path('ensure-dev-zone', 'tesla-gps-save-mongodb')
        try:
            client = pymongo.MongoClient("mongodb+srv://mababio:aCyCNd9OcpDCOovX@home-automation.mplvx.mongodb.net/?retryWrites=true&w=majority", server_api=ServerApi('1'))
            self.tesla_database = client['tesla']
        except Exception as e:
            logger.error("DBClient__init__::::: Issue with connecting to Mongodb: " + str(e))
            raise

    def get_tesla_database(self):
        try:
            return self.tesla_database
        except Exception as e:
            logger.error("get_tesla_database::::: Error getting mongodb client conn to DB " + str(e))

    def set_ifttt_trigger_lock(self,bolval):
        myquery = {"_id": "IFTTT_TRIGGER_LOCK"}
        newvalues = {"$set": {"lock": bolval}}
        self.tesla_database['tesla_trigger'].update_one(myquery, newvalues)
        logger.debug('set_ifttt_trigger_lock::::: Updating ifttt_trigger_lock value to' + str(bolval))

    def set_door_close_status(self, reason):
        myquery = {"_id": "garage"}
        newvalues = {"$set": {"closed_reason": reason}}
        self.tesla_database['garage'].update_one(myquery, newvalues)
        logger.debug('set_door_close_status::::: Updating door_close_status value to' + str(reason))

    def get_ifttt_trigger_lock(self):
        logger.debug('get_ifttt_trigger_lock::::: Getting ifttt_trigger_lock value')
        return self.tesla_database['tesla_trigger'].find_one()['lock']

    def get_door_close_status(self):
        logger.debug('get_door_close_status::::: get_door_close_status: Getting door_close_status value')
        return self.tesla_database['garage'].find_one()['closed_reason']

    def __get_saved_location(self):
        return self.tesla_database['tesla_location'].find_one({'_id':'current'})

    def save_location(self, json_lat_lon):
        if isinstance(json_lat_lon, dict):
            data_str = json.dumps(json_lat_lon)
        else:
            logger.error("save_location::::: Type dict was not provided")
            raise TypeError("save_location::::: Type dict was not provided")
        future = self.publisher.publish(self.tesla_gps_save_mongodb_topic, data_str.encode("utf-8"))
        logger.info('save_location::::: sent latlon to pubsub')
        return future






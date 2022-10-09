from enum import Enum
import requests
from config import settings
from util.logs import logger
from util.notification import send_push_notification
from util.db_mongo import DBClient


class GarageCloseReason(Enum):
    DRIVE_AWAY = 'DRIVE_AWAY'
    DRIVE_HOME = 'DRIVE_HOME'
    NOT_SURE = 'NOT_SURE'


class GarageOpenReason(Enum):
    DRIVE_HOME = 'DRIVE_HOME'
    DRIVE_AWAY = 'DRIVE_AWAY'
    NOT_SURE = 'NOT_SURE'


def garage_is_open():
    return False if requests.post(settings['production']['URL']['myq_garage'], json={"isopen": ''}).json()['isopen'] \
                    == 'closed' else True


def open_garage():
    send_push_notification('Would of opened the garage')
    return True
    try:
        DBClient().publish_open_garage()
        #return_val = requests.get(settings['development']['URL']['myq_garage'])
        ###set_open___reason(GarageOpenReason.DRIVE_HOME, db)     DONT USE THIS ...
        # FUNCTION DOES NOT EXIST AND FLAG HAS BEEN SET IN trigger_tesla_home_automation
        return True if return_val else False
    except Exception as e:
        logger.error('open_garage::::: Issue with opening the garage::::: ' + str(e))


def close_garage():
    try:
        return requests.post(settings['production']['URL']['myq_garage'], json={"state": 'close'}).json()
    except Exception as e:
        logger.error('open_garage::::: Issue with opening the garage::::: ' + str(e))



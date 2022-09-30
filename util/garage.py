from enum import Enum
import requests
from config import settings
from util.logs import logger
# import util.db_mongo as db_mongo


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


def set_open_reason(garage_open_reason, db):
    if isinstance(garage_open_reason, GarageOpenReason):
        db.set_door_open_status(garage_open_reason.value)
    else:
        logger.error('set_open_reason::::: Issue with input given')
        raise TypeError('set_open_reason::::: GarageOpenReason Enum type was not provided')


def set_close_reason(garage_close_reason, db):
    if isinstance(garage_close_reason, GarageCloseReason):
        db.set_door_close_status(garage_close_reason.value)
    else:
        logger.error('set_close_reason::::: Issue with input given')
        raise TypeError('set_close_reason::::: GarageCloseReason Enum type was not provided')


def open_garage(db):
    try:
        return_val = requests.get(settings['development']['URL']['myq_garage'])
        set_open_reason(GarageOpenReason.DRIVE_HOME, db)
        return True if return_val else False
    except Exception as e:
        logger.error('open_garage::::: Issue with opening the garage::::: ' + str(e))


def close_garage():
    try:
        return requests.post(settings['production']['URL']['myq_garage'], json={"state": 'close'}).json()
    except Exception as e:
        logger.error('open_garage::::: Issue with opening the garage::::: ' + str(e))




# db1 = db_mongo.DBClient()
# set_close_reason(GarageCloseReason.DRIVE_AWAY, db1)

requests.post(settings['production']['URL']['myq_garage'], json={"state": 'close'}).json()


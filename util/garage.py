from enum import Enum
import requests
from config import settings
from util.logs import logger
from util.notification import send_push_notification


class GarageCloseReason(Enum):
    DRIVE_AWAY = 'DRIVE_AWAY'
    DRIVE_HOME = 'DRIVE_HOME'
    NOT_SURE = 'NOT_SURE'


class GarageOpenReason(Enum):
    DRIVE_HOME = 'DRIVE_HOME'
    DRIVE_AWAY = 'DRIVE_AWAY'
    NOT_SURE = 'NOT_SURE'

# TODO: May be moving away from myq api soon
def garage_is_open():
    return False if requests.post(settings['production']['URL']['myq_garage'], json={"isopen": ''}).json()['isopen'] \
                    == 'closed' else True







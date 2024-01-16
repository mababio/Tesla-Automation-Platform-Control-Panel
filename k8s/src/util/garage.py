"""
Author:     Michael Ababio
Date:       08/08/2022
Project:    Tesla Home Automation
File:       garage.py
Purpose: Interface with garage services. To open and close garage door and get state of garage door.
"""

import os
import requests
import notification
from logs import logger

try:
    GARAGE_SERVICES_BASE_URL = os.environ["GARAGE_SERVICES_BASE_URL"]
except KeyError:
    logger.error('garage.py::::: GARAGE_SERVICES_BASE_URL not set')
    raise


def garage_is_open():
    """
    Check if garage is open
    :return:
    """
    notification.send_push_notification('Checking if garage door is open')
    try:
        garage_state = requests.get(f'{GARAGE_SERVICES_BASE_URL}/get_state', timeout=15).json()
        match garage_state:
            case 'opened':
                return True
            case 'closed':
                return False
            case _:
                notification.send_push_notification('garage_is_open:::: Issue with garage services')
                raise TypeError(f'garage_is_open:::: Return type from garage services is not valid.'
                                f' this was returned: {garage_state}')
    except Exception as e:
        logger.error('garage_is_open:::: Issue with garage services %s', str(e))
        notification.send_push_notification(f'garage_is_open::::'
                                            f' Issue with garage services {str(e)}')
        raise


def request_open():
    """
    Request to open garage
    :return:
    """
    if garage_is_open():
        logger.info("Garage is open already! request to open has been ignored")
        notification.send_push_notification('Garage is open already!'
                                            ' request to open has been ignored')
        return {"message": "Garage is opened already! request to open has been ignored"}
    logger.info("Opening Garage!")
    notification.send_push_notification('Opening Garage!')
    return requests.put(f'{GARAGE_SERVICES_BASE_URL}/request_garage_change/open', timeout=15)


def request_close():
    """
    Request to close garage
    :return:
    """
    if not garage_is_open():
        logger.info("Garage is closed already! Request to closed has been ignored")
        notification.send_push_notification('Garage is closed already! '
                                            'request to closed has been ignored')
        return {"message": "Garage is closed already! request to open has been ignored"}
    logger.info("Closing Garage!")
    notification.send_push_notification('Garage is open, closing garage now ...')
    return requests.put(f'{GARAGE_SERVICES_BASE_URL}/request_garage_change/close', timeout=15)


if __name__ == "__main__":
    print(garage_is_open())

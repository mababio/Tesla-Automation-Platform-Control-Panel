import os
import sys
import notification
from logs import logger
sys.path.append('../')
import requests

GARAGE_SERVICES_BASE_URL = os.environ.get("GARAGE_SERVICES_BASE_URL")


def garage_is_open():
    notification.send_push_notification('Checking if garage door is open')
    try:
        garage_state = requests.get(f'{GARAGE_SERVICES_BASE_URL}/get_state').json()
        match garage_state:
            case 'opened':
                return True
            case 'closed':
                return False
            case _:
                notification.send_push_notification(f'garage_is_open:::: Issue with garage services ')
                raise Exception(f'garage_is_open:::: Issue with garage services')
    except Exception as e:
        logger.error(f'garage_is_open:::: Issue with garage services {str(e)}')
        notification.send_push_notification(f'garage_is_open:::: Issue with garage services {str(e)}')
        raise


def request_open():
    if garage_is_open():
        logger.info("Garage is open already! request to open has been ignored")
        notification.send_push_notification('Garage is open already! request to open has been ignored')
        return {"message": "Garage is opened already! request to open has been ignored"}
    else:
        logger.info("Opening Garage!")
        notification.send_push_notification('Opening Garage!')
        return requests.get(f'{GARAGE_SERVICES_BASE_URL}/set_state/open')


def request_close():
    if not garage_is_open():
        logger.info("Garage is closed already! Request to closed has been ignored")
        notification.send_push_notification('Garage is closed already! request to closed has been ignored')
        return {"message": "Garage is closed already! request to open has been ignored"}
    else:
        logger.info("Closing Garage!")
        notification.send_push_notification('Garage is open, closing garage now ...')
        return requests.get(f'{GARAGE_SERVICES_BASE_URL}/set_state/close')


if __name__ == "__main__":
    print(garage_is_open())

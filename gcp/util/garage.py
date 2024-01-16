import time
from enum import Enum
import sys
sys.path.append('../../')
from gcp.config import settings
from paho.mqtt import client as mqtt_client
import random
import asyncio
from aiohttp import ClientSession
import pymyq
from gcp.util.logs import logger
from gcp import util as notification


class GarageCloseReason(Enum):
    DRIVE_AWAY = 'DRIVE_AWAY'
    DRIVE_HOME = 'DRIVE_HOME'
    NOT_SURE = 'NOT_SURE'


class GarageOpenReason(Enum):
    DRIVE_HOME = 'DRIVE_HOME'
    DRIVE_AWAY = 'DRIVE_AWAY'
    NOT_SURE = 'NOT_SURE'


broker = settings['mqtt']['broker']
port = 8883
topic = "garage/command"
# generate client ID with pub prefix randomly
client_id = f'garage-Tesla-Automation-Platform-{random.randint(0, 100)}'
username = settings['mqtt']['username']
password = settings['mqtt']['password']


async def get_garage_state() -> None:
    """Create the aiohttp session and run."""
    async with ClientSession() as websession:
        myq = await pymyq.login(settings['garage']['username'], settings['garage']['password'], websession)
        print(myq)
        # devices = myq.covers
        # return devices['CG085035767B'].state


def connect_mqtt():
    try:
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
                notification.send_push_notification("Connected to MQTT Broker!")
                logger.info("MQTT Connected")
            else:
                print("Failed to connect, return code %d\n", rc)
                logger.error("Failed to connect to MQTT")
                notification.send_push_notification("Failed to connect to MQTT")
        client = mqtt_client.Client(client_id)
        client.tls_set(ca_certs='/app/src/mqtt.crt')
        client.username_pw_set(username, password)
        client.on_connect = on_connect
        client.connect(broker, port)
        return client
    except Exception as e:
        notification.send_push_notification("Getting error connecting to MQTT: {}".format(str(e)))


# TODO: May be moving away from myq api soon
def garage_is_open():
    notification.send_push_notification('Checking if garage door is open')
    garage_state = asyncio.run(get_garage_state())
    return False if garage_state == 'closed' else True


def request_open():
    if garage_is_open():
        logger.info("Garage is open already! request to open has been ignored")
        notification.send_push_notification('Garage is open already! request to open has been ignored')
        return False
    else:
        logger.info("Opening Garage!")
        notification.send_push_notification('Opening Garage!')
        client = connect_mqtt()
        client.loop_start()
        time.sleep(1)
        # client.publish(topic, "open")
        client.loop_stop()


def request_close():
    if not garage_is_open():
        logger.info("Garage is closed already! Request to closed has been ignored")
        notification.send_push_notification('Garage is closed already! request to closed has been ignored')
    else:
        logger.info("Closing Garage!")
        client = connect_mqtt()
        client.loop_start()
        # client.publish(topic, "closed")
        client.loop_stop()


if __name__ == "__main__":
    print(garage_is_open())
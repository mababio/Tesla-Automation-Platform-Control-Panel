import os
from enum import Enum
import sys
import notification
from logs import logger

sys.path.append('../')
from paho.mqtt import client as mqtt_client
import random
from aiohttp import ClientSession
import pymyq

# from utils.logs import logger
# import utils.notification as notification


MQTT_BROKER = os.environ.get("MQTT_BROKER")
MQTT_USER = os.environ.get("MQTT_USER")
MQTT_PASSWORD =os.environ.get("MQTT_PASSWORD")
TESLA_USERNAME = os.environ.get("TESLA_USERNAME")
MQ_USER = os.environ.get("MQ_USER")
MQ_PASSWORD = os.environ.get('MQ_PASSWORD')
GMAPS_KEY = os.environ.get("GMAPS_KEY")


class GarageCloseReason(Enum):
    DRIVE_AWAY = 'DRIVE_AWAY'
    DRIVE_HOME = 'DRIVE_HOME'
    NOT_SURE = 'NOT_SURE'


class GarageOpenReason(Enum):
    DRIVE_HOME = 'DRIVE_HOME'
    DRIVE_AWAY = 'DRIVE_AWAY'
    NOT_SURE = 'NOT_SURE'


broker = MQTT_BROKER
port = 8883
topic = "garage/command"
# generate client ID with pub prefix randomly
client_id = f'garage-Tesla-Automation-Platform-{random.randint(0, 100)}'
username = MQTT_USER
password = MQTT_PASSWORD


async def get_garage_state() -> None:
    try:
        """Create the aiohttp session and run."""
        async with ClientSession() as websession:
            myq = await pymyq.login(MQ_USER, MQ_PASSWORD, websession)
            devices = myq.covers
            return devices['CG085035767B'].state
    except Exception as e:
        notification.send_push_notification('Error with garage my API, but going to proceed')
        return None


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
        client.tls_set(ca_certs='/app/mqtt_crt/mqtt.crt')
        client.username_pw_set(username, password)
        client.on_connect = on_connect
        client.connect(broker, port)
        return client
    except Exception as e:
        notification.send_push_notification("Getting error connecting to MQTT: {}".format(str(e)))


# TODO: May be moving away from myq api soon
def garage_is_open():
    notification.send_push_notification('Checking if garage door is open')
    return False
    # TODO: Issue with pymq https://github.com/arraylabs/pymyq/issues/187
    # TODO: Appears the issue is fixed, but now getting 429 error. too many requests
    # Below lines commented out until issue is resolved
    # garage_state = asyncio.run(get_garage_state())
    # return False if garage_state == 'closed' else True


def request_open():
    if garage_is_open():
        logger.info("Garage is open already! request to open has been ignored")
        notification.send_push_notification('Garage is open already! request to open has been ignored')
        return False
    else:
        logger.info("Opening Garage!")
        notification.send_push_notification('Opening Garage!')
        # TODO:  Once I get this app into kube, than I will find a good mqtt and uncommet lines below
        # client = connect_mqtt()
        # client.loop_start()
        # time.sleep(1)
        # # client.publish(topic, "open")
        # client.loop_stop()


def request_close():
    if not garage_is_open():
        logger.info("Garage is closed already! Request to closed has been ignored")
        notification.send_push_notification('Garage is closed already! request to closed has been ignored')
    else:
        logger.info("Closing Garage!")
        # TODO:  Once I get this app into kube, than I will find a good mqtt and uncommet lines below
        # client = connect_mqtt()
        # client.loop_start()
        # # client.publish(topic, "closed")
        # client.loop_stop()


if __name__ == "__main__":
    print(garage_is_open())

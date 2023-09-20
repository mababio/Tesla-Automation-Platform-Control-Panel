from enum import Enum
import requests
from config import settings
from paho.mqtt import client as mqtt_client
import random

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


broker = settings['mqtt']['broker']
port = 8883
topic = "garage/command"
# generate client ID with pub prefix randomly
client_id = f'garage-Tesla-Automation-Platform-{random.randint(0, 100)}'
username = settings['mqtt']['username']
password = settings['mqtt']['password']


def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
            logger.info("MQTT Connected")
        else:
            print("Failed to connect, return code %d\n", rc)
            logger.error("Failed to connect to MQTT")

    client = mqtt_client.Client(client_id)
    client.tls_set(ca_certs='./server-ca.crt')
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


# TODO: May be moving away from myq api soon
def garage_is_open():
    return False if requests.post(settings['production']['URL']['myq_garage'], json={"isopen": ''}).json()['isopen'] \
                    == 'closed' else True


def request_open():
    client = connect_mqtt()
    client.loop_start()
    client.publish(topic, "open")
    client.loop_stop()


def request_close():
    client = connect_mqtt()
    client.loop_start()
    client.publish(topic, "closed")
    client.loop_stop()

import os
import requests
import redis

try:
    TESLA_DATA_SERVICES_BASE_URL = os.environ["TESLA_DATA_SERVICES_BASE_URL"]
    VIN = os.environ["VIN"]
except KeyError:
    print('utils.py::::: TESLA_DATA_SERVICES_BASE_URL or VIN not set')
    raise


def get_car_document(vin=VIN):
    """
    Gets Mongodb document that represents the state of car. Database request is handled by Fast API
    :return: JSON object representing MongoDb Car document
    """
    return requests.get(f"{TESLA_DATA_SERVICES_BASE_URL}/api/car/get/car/{vin}", timeout=15).json()


def set_car_document(param, value=None, vin=VIN):
    if value is not None:
        return requests.put(f"{TESLA_DATA_SERVICES_BASE_URL}/api/car/update/{param}/{vin}/{value}", timeout=15)
    return requests.put(f"{TESLA_DATA_SERVICES_BASE_URL}/api/car/update/{param}", timeout=15)


def schedule_proximity_task(delay_minutes):
    """
    Function that schedules a HTTP request for car proximity
    :param delay_minutes: how far into the future do you want to run a proximity checker on the car
    """
    r = redis.Redis(
        host='redis-pub-sub',
        port=6379,
        decode_responses=True
    )
    r.publish('job-scheduler', f"{'delay': {delay_minutes} , 'task': 'CHECK_PROXIMITY'}")


if __name__ == "__main__":
    print(get_car_document())

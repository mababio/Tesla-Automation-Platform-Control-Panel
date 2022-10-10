import random
import time
import pymongo
from datetime import datetime
from pytz import timezone
from util import db_mongo, garage

obj = db_mongo.DBClient()
db = obj.get_tesla_database()


def get_db_latlon_age():
    est = timezone('US/Eastern')
    db_latlon_timestamp_est = db['tesla_location'].find_one({'_id': 'current'})['timestamp'].split('.')[0]
    db_latlon_timestamp_est_str = str(db_latlon_timestamp_est)
    db_latlon_timestamp_datetime_obj = datetime.strptime(db_latlon_timestamp_est_str, "%Y-%m-%d %H:%M:%S")

    current_timestamp_est_datetime_obj = datetime.now(est)
    current_timestamp_est_datetime_obj_formatted = str(current_timestamp_est_datetime_obj).split('.')[0]
    accepted_current_timestamp_est_datetime_obj = datetime.strptime(current_timestamp_est_datetime_obj_formatted,
                                                                "%Y-%m-%d %H:%M:%S")

    timelapse = accepted_current_timestamp_est_datetime_obj - db_latlon_timestamp_datetime_obj
    return int(timelapse.total_seconds()/60)  # this is in minutes


def test_get_tesla_database():
    assert type(db) is pymongo.database.Database
    assert db.name == 'tesla'


def test_set_tesla_location_is_home_value():
    original_value = obj.get_tesla_location_is_home_value()
    obj.set_tesla_location_is_home_value(True)
    assert obj.get_tesla_location_is_home_value() is True
    obj.set_tesla_location_is_home_value(False)
    assert obj.get_tesla_location_is_home_value() is False
    obj.set_tesla_location_is_home_value(original_value)


def test_set_ifttt_trigger_lock():
    remember_original_value = obj.get_ifttt_trigger_lock()
    obj.set_ifttt_trigger_lock('False')
    assert obj.get_ifttt_trigger_lock() == 'False'
    obj.set_ifttt_trigger_lock('True')
    assert obj.get_ifttt_trigger_lock() == 'True'
    obj.set_ifttt_trigger_lock(remember_original_value)


def test_set_door_close_status():
    original_value = obj.get_door_close_status()
    if original_value == garage.GarageCloseReason.DRIVE_AWAY.value:
        original_value = garage.GarageCloseReason.DRIVE_AWAY
    else:
        original_value = garage.GarageCloseReason.DRIVE_HOME

    obj.set_door_close_status(garage.GarageCloseReason.DRIVE_HOME)
    assert obj.get_door_close_status() == garage.GarageCloseReason.DRIVE_HOME.value
    obj.set_door_close_status(garage.GarageCloseReason.DRIVE_AWAY)
    assert obj.get_door_close_status() == garage.GarageCloseReason.DRIVE_AWAY.value

    obj.set_door_close_status(original_value)


def test_set_door_open_status():
    original_value = obj.get_door_open_status()
    if original_value == garage.GarageOpenReason.DRIVE_AWAY.value:
        original_value = garage.GarageOpenReason.DRIVE_AWAY
    else:
        original_value = garage.GarageOpenReason.DRIVE_HOME

    obj.set_door_open_status(garage.GarageOpenReason.DRIVE_HOME)
    assert obj.get_door_open_status() == garage.GarageOpenReason.DRIVE_HOME.value
    obj.set_door_open_status(garage.GarageOpenReason.DRIVE_AWAY)
    assert obj.get_door_open_status() == garage.GarageOpenReason.DRIVE_AWAY.value
    obj.set_door_open_status(original_value)


def test_get_ifttt_trigger_lock():
    original_value = obj.get_ifttt_trigger_lock()
    assert obj.get_ifttt_trigger_lock() == 'False' or 'True'
    obj.set_ifttt_trigger_lock('False')
    assert obj.get_ifttt_trigger_lock() == 'False'
    obj.set_ifttt_trigger_lock(original_value)


def test_get_door_close_status():
    original_value = obj.get_door_close_status()
    if original_value == garage.GarageCloseReason.DRIVE_AWAY.value:
        original_value = garage.GarageCloseReason.DRIVE_AWAY
    else:
        original_value = garage.GarageCloseReason.DRIVE_HOME
    assert obj.get_door_close_status() == garage.GarageCloseReason.DRIVE_AWAY.value or \
           garage.GarageCloseReason.DRIVE_HOME.value
    obj.set_door_close_status(garage.GarageCloseReason.DRIVE_AWAY)
    assert obj.get_door_close_status() == garage.GarageCloseReason.DRIVE_AWAY.value
    obj.set_door_close_status(original_value)


def test_get_door_open_status():
    original_value = obj.get_door_open_status()
    if original_value == garage.GarageOpenReason.DRIVE_AWAY.value:
        original_value = garage.GarageOpenReason.DRIVE_AWAY
    else:
        original_value = garage.GarageOpenReason.DRIVE_HOME
    assert obj.get_door_open_status() == garage.GarageOpenReason.DRIVE_AWAY.value or \
           garage.GarageOpenReason.DRIVE_HOME.value
    obj.set_door_open_status(garage.GarageOpenReason.DRIVE_AWAY)
    assert obj.get_door_open_status() == garage.GarageOpenReason.DRIVE_AWAY.value
    obj.set_door_open_status(original_value)


def test_get_saved_location():
    assert type(obj.get_saved_location()) is dict
    assert type(obj.get_saved_location()['lat']) is float
    assert type(obj.get_saved_location()['lon']) is float
    assert type(obj.get_saved_location()['is_home']) is bool
    assert type(obj.get_saved_location()['timestamp']) is str
    timestamp_from_db = obj.get_saved_location()['timestamp'].split('.')[0]
    timestamp_str = str(timestamp_from_db)
    assert type(datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")) is datetime


def test_save_location():
    random_lat = random.uniform(30, 100)
    random_lon = random.uniform(-30, -100)
    random_gps_dict = {'lat': random_lat, 'lon': random_lon}
    obj.save_location(random_gps_dict)
    time.sleep(5)
    db_returned_gps = obj.get_saved_location()
    assert random_lat == db_returned_gps['lat']
    assert random_lon == db_returned_gps['lon']
    assert get_db_latlon_age() < 1
    assert obj.is_climate_turned_on_via_automation() is False
    assert obj.climate_turned_on_via_automation_before() is False


def test_is_climate_turned_on_via_automation():
    assert type(obj.is_climate_turned_on_via_automation()) is bool

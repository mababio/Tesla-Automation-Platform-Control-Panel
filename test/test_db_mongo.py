import pymongo

from util import db_mongo, garage

obj = db_mongo.DBClient()


def test_get_tesla_database():
    db = obj.get_tesla_database()
    assert type(db) is pymongo.database.Database
    assert db.name == 'tesla'


def test_set_tesla_location_is_home_value():
    obj.set_tesla_location_is_home_value(True)
    assert obj.get_tesla_location_is_home_value() is True
    obj.set_tesla_location_is_home_value(False)
    assert obj.get_tesla_location_is_home_value() is False


def test_set_ifttt_trigger_lock():
    remember_original_value = obj.get_ifttt_trigger_lock()
    obj.set_ifttt_trigger_lock('False')
    assert obj.get_ifttt_trigger_lock() == 'False'
    obj.set_ifttt_trigger_lock('True')
    assert obj.get_ifttt_trigger_lock() == 'True'
    obj.set_ifttt_trigger_lock(remember_original_value)


def test_set_door_close_status():
    obj.set_door_close_status(garage.GarageCloseReason.DRIVE_HOME)
    assert obj.get_door_close_status() == garage.GarageCloseReason.DRIVE_HOME.value
    obj.set_door_close_status(garage.GarageCloseReason.DRIVE_AWAY)
    assert obj.get_door_close_status() == garage.GarageCloseReason.DRIVE_AWAY.value

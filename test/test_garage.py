import time

from util import garage
from util import db_mongo


db_client = db_mongo.DBClient()
db = db_client.tesla_database


def test_garage_is_open():
    assert type(garage.garage_is_open()) is bool


def test_open_garage():
    assert False


def test_close_garage():
    assert False


# def test_set_open_reason():
#     if db_client.get_door_open_status() == garage.GarageOpenReason.DRIVE_HOME.value:
#         garage.set_open_reason(garage.GarageOpenReason.DRIVE_AWAY, db_client)
#         assert db_client.get_door_open_status() != garage.GarageOpenReason.DRIVE_HOME.value
#         garage.set_open_reason(garage.GarageOpenReason.DRIVE_HOME, db_client)
#         assert db_client.get_door_open_status() == garage.GarageOpenReason.DRIVE_HOME.value
#     else:
#         db_client.set_door_open_status(garage.GarageOpenReason.DRIVE_HOME)
#         assert db_client.get_door_open_status() == garage.GarageOpenReason.DRIVE_HOME.value
#         db_client.set_door_open_status(garage.GarageOpenReason.DRIVE_AWAY)
#         assert db_client.get_door_open_status() == garage.GarageOpenReason.DRIVE_AWAY.value



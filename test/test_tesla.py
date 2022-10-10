from datetime import datetime

from pytz import timezone

from util import tesla
from util import db_mongo
from util import garage


obj = tesla.Tesla()
db = db_mongo.DBClient()


def get_db_latlon_age():
    est = timezone('US/Eastern')
    db_latlon_timestamp_est = db.tesla_database['tesla_location'].find_one({'_id': 'current'})['timestamp'].split('.')[0]
    db_latlon_timestamp_est_str = str(db_latlon_timestamp_est)
    db_latlon_timestamp_datetime_obj = datetime.strptime(db_latlon_timestamp_est_str, "%Y-%m-%d %H:%M:%S")

    current_timestamp_est_datetime_obj = datetime.now(est)
    current_timestamp_est_datetime_obj_formatted = str(current_timestamp_est_datetime_obj).split('.')[0]
    accepted_current_timestamp_est_datetime_obj = datetime.strptime(current_timestamp_est_datetime_obj_formatted,
                                                                    "%Y-%m-%d %H:%M:%S")

    timelapse = accepted_current_timestamp_est_datetime_obj - db_latlon_timestamp_datetime_obj
    return int(timelapse.total_seconds()/60)  # this is in minutes


def test_is_tesla_moving():
    assert type(obj.is_tesla_moving()) is bool


def test_is_close():
    assert type(obj.is_close()) is bool
    if not obj.is_close():
        assert db.get_door_close_status() == garage.GarageCloseReason.DRIVE_AWAY.value
    else:
        assert db.get_door_close_status() == garage.GarageCloseReason.DRIVE_HOME.value


def test_get_proximity():
    testing_dict = obj.get_proximity()
    assert type(testing_dict) is dict
    assert type(testing_dict['difference']) is float


def test_get_location():
    testing_dict = obj.get_location()
    assert type(testing_dict) is dict
    assert type(testing_dict['lat']) is float
    assert type(testing_dict['lon']) is float
    if obj.is_tesla_moving():
        assert get_db_latlon_age() <= 1
        assert db.is_climate_turned_on_via_automation() is False
    elif get_db_latlon_age() > 5:
        assert db.climate_turned_on_via_automation_before() is True or \
               db.is_climate_turned_on_via_automation() is True
    else:
        assert db.is_climate_turned_on_via_automation() is False


def test_is_on_home_street():
    if obj.is_on_home_street():
        assert obj.is_close() is True
    else:
        assert obj.is_close() is False




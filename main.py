import os
from flask import Flask
from flask import g
from flask_executor import Executor
from util.db_mongo import DBClient
from util import tap
from util import notification
from util.logs import logger
import util.garage as garage
from util.tesla import Tesla

app = Flask(__name__)
executor = Executor(app)


@app.before_request
def before_request():
    try:
        g.db = DBClient()
    except Exception as e:
        notification.send_push_notification('Faced DB connectivity issue' + str(e))
        logger.error('before_request::::: Faced DB connectivity issue' + str(e))
        raise


@app.route("/open")
def kick_off_job_ifttt_open_bg():
    logger.info('kick_off_job_ifttt_open_bg: start of the /open flask route')
    if g.db.get_tesla_database()['tesla_trigger'].find_one()['lock'] == 'False':
        g.db.get_tesla_database()['tesla_trigger'].update_one({"_id": "IFTTT_TRIGGER_LOCK"}, {"$set": {"lock": "True"}})
        executor.submit(tesla_automation)
        return 'Scheduled a job'
    else:
        notification.send_push_notification("Process is already running")
        return 'Process is already running'


@app.route("/close")
def kick_off_job_ifttt_close_bg():
    if g.db.get_door_close_status() == 'DRIVE_HOME':
        executor.submit(garage_door_closed)
        notification.send_push_notification('Car has arrive and door was closed')
        return 'Car has arrive and door was closed'
    else:
        notification.send_push_notification('Garage Door closed')
        return 'Garage Door closed'


def garage_door_closed():
    myquery_ifttt_trigger_lock = {"_id": "IFTTT_TRIGGER_LOCK"}
    ct = {"$set": {"lock": "False"}}
    myquery_garage_closed_reason = {"_id": "garage"}
    new_values_ifttt_trigger_lock = {"$set": {"locked_reason": " "}}

    g.db.get_tesla_database()['tesla_trigger'].update_one(myquery_ifttt_trigger_lock, ct)
    g.db.get_tesla_database()['garage'].update_one(myquery_garage_closed_reason, new_values_ifttt_trigger_lock)


def tesla_automation():
    tesla_tap = tap.TAP()
    professor = Tesla()
    if tesla_tap.confirmation_before_armed():
        notification.send_push_notification('Trigger tesla home automation!')
        logger.info('Trigger tesla home automation!')
        tesla_tap.tesla_home_automation_engine()
        notification.send_push_notification('automation Done')
    elif garage.garage_is_open():
        notification.send_push_notification(' Garage door has been open for 5 mins. would your like to close, '
                                            'leave open or are you'
                                            ' loading the bikes??')
        notification.send_push_notification('automation Done')
    elif professor.is_on_home_street:
        notification.send_push_notification('Still on Arcui ct')
        notification.send_push_notification('automation Done')
    tesla_tap.cleanup()


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

import os
from flask import Flask
from flask import g
from flask_executor import Executor
from util.db_mongo import DBClient
from util import tap
from util import notification
from util.logs import logger

app = Flask(__name__)
executor = Executor(app)


@app.before_request
def before_request():
    try:
        g.db = DBClient()
    except Exception as e:
        notification.send_push_notification('Faced DB connectivity issue' + str(e))
        raise


@app.route("/open")
def kick_off_job_ifttt_open_bg():
    logger.debug('kick_off_job_ifttt_open_bg: start of the /open flask route')
    if g.db.get_tesla_database()['tesla_trigger'].find_one()['lock'] == 'False':
        myquery = {"_id": "IFTTT_TRIGGER_LOCK"}
        newvalues = {"$set": {"lock": "True"}}
        g.db.get_tesla_database()['tesla_trigger'].update_one(myquery, newvalues)
        executor.submit(tesla_automation)
        return 'Scheduled a job'
    else:
        notification.send_push_notification("Process is already running")
        return 'Process is already running'


@app.route("/close")
def kick_off_job_ifttt_close_bg():
    if g.db.get_door_close_status() == 'came_home':
        executor.submit(garage_door_closed)
        notification.send_push_notification('Car has arrive and door was closed')
        return 'Car has arrive and door was closed'
    else:
        notification.send_push_notification('Door was not closed b/c car came home')
        return 'Door was not closed b/c car came home'


def garage_door_closed():
    myquery_ifttt_trigger_lock = {"_id": "IFTTT_TRIGGER_LOCK"}
    ct = {"$set": {"lock": "False"}}
    myquery_garage_closed_reason = {"_id": "garage"}
    newvalues_ifttt_trigger_lock = {"$set": {"locked_reason": " "}}

    g.db.get_tesla_database()['tesla_trigger'].update_one(myquery_ifttt_trigger_lock, ct)
    g.db.get_tesla_database()['garage'].update_one(myquery_garage_closed_reason, newvalues_ifttt_trigger_lock)


def tesla_automation():
    tesla_tap = tap.TAP()
    if tesla_tap.confirmation_before_armed():
        notification.send_push_notification('trigger tesla home automation!')
        tesla_tap.tesla_home_automation_engine()
        notification.send_push_notification('automation Done')
    elif tesla_tap.garage_still_open:
        notification.send_push_notification(' Garage door has been open for 5 mins. would your like to close, '
                                            'leave open or are you'
                                            ' loading the bikes??')
        notification.send_push_notification('automation Done')
    elif tesla_tap.stil_on_home_street:
        notification.send_push_notification('limit of 5 mins has been meet or still on Arcui ct')
        notification.send_push_notification('automation Done')
    tesla_tap.cleanup()


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

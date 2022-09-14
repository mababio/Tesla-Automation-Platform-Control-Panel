import os
from flask import Flask
from flask import g
from flask_executor import Executor
#from app.db_mongo import db_client
from util.db_mongo import db_client
from util import tap
from util import sms

app = Flask(__name__)
executor = Executor(app)


@app.before_request
def before_request():
    g.db = db_client()


@app.route("/open")
def kick_off_job_ifttt_open_bg():
    if g.db.get_tesla_database()['tesla_trigger'].find_one()['lock'] == 'False':
        myquery = {"_id": "IFTTT_TRIGGER_LOCK"}
        newvalues = {"$set": {"lock": "True"}}
        g.db.get_tesla_database()['tesla_trigger'].update_one(myquery, newvalues)
        executor.submit(tesla_automation)
        return 'Scheduled a job'
    else:
        sms.send_sms("Process is already running")
        return 'Process is already running'


@app.route("/close")
def kick_off_job_ifttt_close_bg():
    if g.db.get_door_close_status() == 'came_home':
        executor.submit(garage_door_closed)
        sms.send_sms('Car has arrive and door was closed')
        return 'Car has arrive and door was closed'
    else:
        sms.send_sms('Door was not closed b/c car came home')
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
        sms.send_sms('trigger tesla home automation!')
        tesla_tap.tesla_home_automation_engine()
        sms.send_sms('automation Done')
    elif tesla_tap.garage_still_open:
        sms.send_sms(' Garage door has been open for 5 mins. would your like to close, '
                     'leave open or are you'
                     ' loading the bikes??')
        sms.send_sms('automation Done')
    elif tesla_tap.stil_on_home_street:
        sms.send_sms('limit of 5 mins has been meet or still on Arcui ct')
        sms.send_sms('automation Done')
    tesla_tap.cleanup()


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

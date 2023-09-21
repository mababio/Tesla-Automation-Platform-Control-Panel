import os
from flask import Flask, g
from flask_executor import Executor
from util.db_mongo import DBClient
from util import tap, notification
from util.logs import logger
import util.garage as garage
import util.gcp_scheduler as scheduler
from util.tesla import Tesla

app = Flask(__name__)
executor = Executor(app)


# TODO: It may be possible to remove IFFTT. Maybe put a listner in the raspi garage setup to always
#  check the door status


# TODO: Not sure if this is the most effient way to connect to DB.
# Everytime a request is made, a new db connection is created


@app.before_request
def before_request():
    """
    logic ran before every HTTP requests. Logs issues when they occur and pushes notification
    """
    try:
        g.db = DBClient()
    except Exception as e:
        notification.send_push_notification('Faced DB connectivity issue' + str(e))
        logger.error('before_request::::: Faced DB connectivity issue' + str(e))
        raise


@app.route("/opened")
def kick_off_job_ifttt_open_bg():
    """
    Event driven function. called when garage door is opened. IFTTT will be triggered to call this function
    :return: String status of function
    """
    logger.info('kick_off_job_ifttt_open_bg: start of the /open flask route')
    if g.db.get_ifttt_trigger_lock() != 'False' or g.db.get_door_close_status() == 'DRIVE_AWAY':
        notification.send_push_notification("Process is already running")
        return 'Process is already running'
    else:
        g.db.set_ifttt_trigger_lock("True")
        executor.submit(tesla_automation)
        notification.send_push_notification("Scheduled a job")
        return 'Scheduled a job'


@app.route("/closed")
def kick_off_job_ifttt_close_bg():
    """
    Event driven function. Called when garage door is closed. IFTTT will be triggered to call this function
    :return: String status of function
    """
    if g.db.get_door_open_status() == 'DRIVE_HOME':
        executor.submit(garage_door_closed)
        notification.send_push_notification('Car has arrive and door was closed')
        return 'Car has arrive and door was closed'
    else:
        notification.send_push_notification('Garage Door closed')
        g.db.publish_validate_state_then_cleanup()
        return 'Garage Door closed'


# TODO: don't clearly see the differency implementation wise between long term kick off and kick_off_job_ifttt_open_bg
@app.route("/long_term")
def kick_off_job_long_term_bg():
    """
    Event Driven function. Fast track way to trigger tesla automation engine for when the car is far away

    :return: String function status
    """
    logger.info('kick_off_job_long_term_bg::::: Kicking off :::::')
    if g.db.get_door_open_status() == 'DRIVE_AWAY' and g.db.get_ifttt_trigger_lock() != "True":
        g.db.set_ifttt_trigger_lock("True")
        tesla_tap = tap.TAP()
        executor.submit(tesla_tap.tesla_home_automation_engine)
        return 'Scheduled a job'
    else:
        logger.error('kick_off_job_long_term_bg::::: Appears car is home and this function should not run')
        notification.send_push_notification('kick_off_job_long_term_bg::::: Appears car is home and this function '
                                            'should not run... '
                                            ' pausing gcp cloud scheulder')
        scheduler.pause_job(scheduler.schedule_Jobs.TESLA_LONG_TERM)

        return 'kick_off_job_long_term_bg::::: Appears car is home and this function should not run'


def garage_door_closed():
    """
    Clean up function. Function that runs when car returns home and garage door closes
    """
    g.db.reset_all_flags_tap_is_complete()


# TODO: update push notification where Arcui is mentioned. parametize on that
def tesla_automation():
    """
    Main Entry way into tesla home automation engine.
    """
    notification.send_push_notification('1!')
    tesla_tap = tap.TAP()
    professor = Tesla()
    notification.send_push_notification('2!')
    if tesla_tap.confirmation_before_armed():
        notification.send_push_notification('9!')
        g.db.tap_set_flags_on()
        notification.send_push_notification('10!')
        notification.send_push_notification('Trigger Tesla home automation!')
        logger.info('Trigger Tesla home automation!')
        tesla_tap.tesla_home_automation_engine()
    elif garage.garage_is_open():
        notification.send_push_notification('11!')
        notification.send_push_notification(' Garage door has been open for a long time. Would your like to close, '
                                            'leave open or are you'
                                            ' loading bikes??')
        g.db.reset_all_flags_tap_is_complete()
    elif professor.is_on_home_street():
        notification.send_push_notification('12!')
        notification.send_push_notification('Still on Arcui ct')
        g.db.reset_all_flags_tap_is_complete()
    else:
        notification.send_push_notification('13!')
        notification.send_push_notification("TAP should of been set!")
        logger.error("tesla_automation::::: TAP should of been set!")
    tesla_tap.cleanup()


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

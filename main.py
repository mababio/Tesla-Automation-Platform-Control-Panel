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
    if g.db.get_ifttt_trigger_lock() != 'False' or g.db.get_door_close_status() == 'DRIVE_AWAY':
        notification.send_push_notification("Process is already running")
        return 'Process is already running'
    else:
        g.db.set_ifttt_trigger_lock("True")
        executor.submit(tesla_automation)
        return 'Scheduled a job'


@app.route("/close")
def kick_off_job_ifttt_close_bg():
    if g.db.get_door_open_status() == 'DRIVE_HOME':
        executor.submit(garage_door_closed)
        notification.send_push_notification('Car has arrive and door was closed')
        return 'Car has arrive and door was closed'
    else:
        notification.send_push_notification('Garage Door closed')
        g.db.publish_validate_state_then_cleanup()
        return 'Garage Door closed'


@app.route("/long_term")
def kick_off_job_long_term_bg():
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


@app.route("/ifttt_unlock_tesla")
def kick_off_ifttt_unlock_tesla():
    try:
        professor = Tesla()
        if professor.is_near():
            professor.unlock_tesla()
            scheduler.enable_job(scheduler.schedule_Jobs.TESLA_LOCK_CAR)
        else:
            notification.send_push_notification("kick_off_ifttt_unlock_tesla::::: "
                                                "Tesla unlock was disable! was triggered "
                                                "while car was not near home")
            logger.error("kick_off_ifttt_unlock_tesla ::::: Triggered while not at home. was ignored")
    except Exception as e:
        notification.send_push_notification('Faced issue  unlocking telsa' + str(e))


def garage_door_closed():
    g.db.reset_all_flags_tap_is_complete()


def tesla_automation():
    tesla_tap = tap.TAP()
    professor = Tesla()
    if tesla_tap.confirmation_before_armed():
        g.db.tap_set_flags_on()
        notification.send_push_notification('Trigger Tesla home automation!')
        logger.info('Trigger Tesla home automation!')
        tesla_tap.tesla_home_automation_engine()
    elif garage.garage_is_open():
        notification.send_push_notification(' Garage door has been open for a long time. Would your like to close, '
                                            'leave open or are you'
                                            ' loading bikes??')
        g.db.reset_all_flags_tap_is_complete()
    elif professor.is_on_home_street():
        notification.send_push_notification('Still on Arcui ct')
        g.db.reset_all_flags_tap_is_complete()
    else:
        notification.send_push_notification("TAP should of been set!")
        logger.error("tesla_automation::::: TAP should of been set!")
    tesla_tap.cleanup()


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

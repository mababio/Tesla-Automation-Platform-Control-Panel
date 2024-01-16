"""
Author:     Michael Ababio
Date:       08/08/2022
Project:    Tesla Home Automation
File:       main.py
Purpose: Main entry point for the application. Contains all the routes for the flask app.
"""

import os
from flask import Flask
from flask_executor import Executor
from util import garage, notification, tap, tesla
from util.logs import logger
from util.utils import get_car_document, set_car_document

app = Flask(__name__)
executor = Executor(app)


@app.route("/opened")
def kick_off_job_ifttt_open_bg():
    """
    Event driven function. called when garage door is opened.
    :return: String status of function
    """
    logger.info('kick_off_job_ifttt_open_bg: start of the /open flask route')
    car_status = get_car_document()
    if car_status['trigger'] or car_status['garageStatus']['door_closed'] == 'DRIVE_AWAY':
        notification.send_push_notification(
            f"Process is already running {car_status['trigger']} and "
            f" {car_status['garageStatus']['door_closed']}")
        return 'Process is already running'
    set_car_document('trigger', True)
    executor.submit(tesla_automation)
    notification.send_push_notification("Scheduled a job")
    return 'Scheduled a job'


@app.route("/closed")
def kick_off_job_ifttt_close_bg():
    """
    Event driven function. Called when garage door is closed.
    :return: String status of function
    """
    if get_car_document()['garageStatus']['door_opened'] == 'DRIVE_HOME':
        executor.submit(garage_door_closed)
        notification.send_push_notification('Car has arrive and door was closed')
        return 'Car has arrive and door was closed'
    notification.send_push_notification('Garage Door closed')
    set_car_document('validate_state')
    return 'Garage Door closed'


# TODO: don't clearly see the difference implementation wise
#  between long term kick off and kick_off_job_ifttt_open_bg
@app.route("/long_term")
def kick_off_job_long_term_bg():
    """
    Event Driven function.
    Fast track way to trigger tesla automation engine for when the car is far away

    :return: String function status
    """
    try:
        car_status = get_car_document()
    except Exception as e:
        logger.error('kick_off_job_long_term_bg::::: Issue getting car status from DB %s', str(e))
        notification.send_push_notification('kick_off_job_long_term_bg::::: '
                                            'Issue getting car status from DB' + str(e))
        raise

    logger.info('kick_off_job_long_term_bg::::: Kicking off :::::')
    if car_status['trigger'] != "True":
        set_car_document('trigger', True)
        tesla_tap = tap.TAP()
        executor.submit(tesla_tap.tesla_home_automation_engine)
        return 'Scheduled a job'
    logger.error('kick_off_job_long_term_bg::::: '
                 'Appears car is home and this function should not run')
    notification.send_push_notification('kick_off_job_long_term_bg::::: '
                                        'Appears car is home and this function '
                                        'should not run... '
                                        ' pausing gcp cloud scheduler')
    return 'kick_off_job_long_term_bg::::: Appears car is home and this function should not run'


def garage_door_closed():
    """
    Clean up function. Function that runs when car returns home and garage door closes
    """
    set_car_document('reset_home')


@app.route('/')
def tesla_automation():
    """
    Main Entry way into tesla home automation engine.
    """
    tesla_tap = tap.TAP()
    professor = tesla.Tesla()
    if tesla_tap.confirmation_before_armed():
        set_car_document('set_flags_on')
        notification.send_push_notification('Trigger Tesla home automation!')
        logger.info('Trigger Tesla home automation!')
        tesla_tap.tesla_home_automation_engine()
    elif garage.garage_is_open():
        notification.send_push_notification(' Garage door has been open '
                                            'for a long time. Would your like to close, '
                                            'leave open or are you'
                                            ' loading bikes??')
        set_car_document('reset_home')
    elif professor.is_on_home_street():
        notification.send_push_notification('Still on home street')
        set_car_document('reset_home')
    else:
        notification.send_push_notification("TAP should of been set!")
        logger.error("tesla_automation::::: TAP should of been set!")
    tesla_tap.cleanup()


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8083)))

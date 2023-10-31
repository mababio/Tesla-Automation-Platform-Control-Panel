from enum import Enum

import requests
from google.cloud import scheduler_v1
from google.protobuf import field_mask_pb2
from gcp.config import settings
from gcp.util.logs import logger
from gcp import util as notification

client = scheduler_v1.CloudSchedulerClient()

sess = requests.Session()
adapter = requests.adapters.HTTPAdapter(max_retries=20)
sess.mount('https://', adapter)
url_tesla_data_services = settings['production']['URL']['tesla_data_services'] + '/api/car'


class schedule_Jobs(Enum):
    TESLA_LONG_TERM = settings['production']['scheduler_job']['tesla_long_term']


def get_cron_format(mins):
    return '*/{mins} * * * *'.format(mins=mins)


# TODO: the second param could be rmeoved. the second param is the db src class. it's needed to set trigger to False.
#  This signifies that the system is free to take on other requests. But this could be done more elegatly.
# TODO: Find a more open source approach to GCP scheduler
def schedule_proximity_job(delay_minutes):
    """
    Function that schedules a HTTP request for car proximity
    :param delay_minutes: how far into the future do you want to run a proximity checker on the car
    :param db: DB object used to set trigger state
    :return: GCP job object
    """
    notification.send_push_notification("Delay for {} minutes".format(delay_minutes))
    job = scheduler_v1.Job()
    job.name = settings['production']['scheduler_job']['tesla_long_term']
    job.schedule = get_cron_format(delay_minutes)
    update_mask = field_mask_pb2.FieldMask(paths=['schedule'])
    request = scheduler_v1.UpdateJobRequest(job=job, update_mask=update_mask)
    job = client.update_job(request=request)
    if job.state is not job.State.ENABLED:
        enable_job(schedule_Jobs.TESLA_LONG_TERM)
    request.post("{}{}{}".format(url_tesla_data_services,"/update/trigger/", True))
    # db.set_ifttt_trigger_lock("False")
    return job


def pause_job(job):
    if isinstance(job, schedule_Jobs):
        request = scheduler_v1.PauseJobRequest(name=job.value, )
        job = client.pause_job(request=request)
        return True if job.state is job.State.PAUSED else False
    else:
        logger.error('disable_job::::: Issue with input given')
        raise TypeError('disable_job::::: Schedule_Jobs Enum type was not provided')


def enable_job(job):
    if isinstance(job, schedule_Jobs):
        request = scheduler_v1.ResumeJobRequest(name=job.value, )
        return client.resume_job(request=request)
    else:
        logger.error('disable_job::::: Issue with input given')
        raise TypeError('disable_job::::: Schedule_Jobs Enum type was not provided')


if __name__ == "__main__":
    enable_job(schedule_Jobs.TESLA_LONG_TERM)

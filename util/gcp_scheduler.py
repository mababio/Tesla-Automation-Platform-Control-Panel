from enum import Enum
from google.cloud import scheduler_v1
from google.protobuf import field_mask_pb2
from config import settings
from util.logs import logger
import util.notification as notification

client = scheduler_v1.CloudSchedulerClient()


class schedule_Jobs(Enum):
    TESLA_LONG_TERM = settings['production']['scheduler_job']['tesla_long_term']


def get_cron_format(mins):
    return '*/{mins} * * * *'.format(mins=mins)


# TODO: the second param could be rmeoved. the second param is the db util class. it's needed to set trigger to False.
#  This signifies that the system is free to take on other requests. But this could be done more elegatly.
def schedule_proximity_job(delay_minutes, db):
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
    db.set_ifttt_trigger_lock("False")
    return job


def pause_job(job):
    if isinstance(job, schedule_Jobs):
        request = scheduler_v1.PauseJobRequest(name=job.value, )
        job = client.pause_job(request=request)
        return True if job.state is job.State.PAUSED else False
    else:
        logger.error('disable_job::::: Issue with input given')
        raise TypeError('disable_job::::: schedule_Jobs Enum type was not provided')


def enable_job(job):
    if isinstance(job, schedule_Jobs):
        request = scheduler_v1.ResumeJobRequest(name=job.value, )
        return client.resume_job(request=request)
    else:
        logger.error('disable_job::::: Issue with input given')
        raise TypeError('disable_job::::: schedule_Jobs Enum type was not provided')


if __name__ == "__main__":
    enable_job(schedule_Jobs.TESLA_LONG_TERM)

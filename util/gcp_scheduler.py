from enum import Enum

from google.cloud import scheduler_v1
from google.protobuf import field_mask_pb2
from config import settings
from util.logs import logger

client = scheduler_v1.CloudSchedulerClient()


class schedule_Jobs(Enum):
    TESLA_LONG_TERM = settings['production']['scheduler_job']['tesla_long_term']
    TESLA_LOCK_CAR = settings['production']['scheduler_job']['tesla_lock_car']


def get_cron_format(mins):
    return '*/{mins} * * * *'.format(mins=mins)


def schedule_proximity_job(delay_mins):
    job = scheduler_v1.Job()
    job.name = settings['production']['scheduler_job']
    job.schedule = get_cron_format(delay_mins)
    update_mask = field_mask_pb2.FieldMask(paths=['schedule'])
    request = scheduler_v1.UpdateJobRequest(job=job, update_mask=update_mask)
    job = client.update_job(request=request)
    if job.state is not job.State.ENABLED:
        enable_job(schedule_Jobs.TESLA_LONG_TERM)
        return job
    else:
        return job


def disable_job(job):
    if isinstance(job, schedule_Jobs):
        request = scheduler_v1.PauseJobRequest(name=job.value,)
        return client.pause_job(request=request)
    else:
        logger.error('disable_job::::: Issue with input given')
        raise TypeError('disable_job::::: schedule_Jobs Enum type was not provided')


def enable_job(job):
    if isinstance(job, schedule_Jobs):
        request = scheduler_v1.ResumeJobRequest(name=job.value,)
        return client.resume_job(request=request)
    else:
        logger.error('disable_job::::: Issue with input given')
        raise TypeError('disable_job::::: schedule_Jobs Enum type was not provided')


if __name__ == "__main__":
    enable_job()

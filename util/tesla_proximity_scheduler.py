from google.cloud import scheduler_v1
from google.protobuf import field_mask_pb2
from config import settings

client = scheduler_v1.CloudSchedulerClient()


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
        enable_job()
        return job
    else:
        return job


def disable_job():
    request = scheduler_v1.PauseJobRequest(name= settings['production']['scheduler_job'],)
    return client.pause_job(request=request)


def enable_job():
    request = scheduler_v1.ResumeJobRequest(name=settings['production']['scheduler_job'],)
    client.resume_job(request=request)


if __name__ == "__main__":
    enable_job()

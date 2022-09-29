from google.cloud import scheduler_v1

def create_scheduler_job():
    """Create a job with an App Engine target via the Cloud Scheduler API"""
    # [START cloud_scheduler_create_job]
    from google.cloud import scheduler

    # Create a client.
    client = scheduler.CloudSchedulerClient()

    # TODO(developer): Uncomment and set the following variables
    project_id = 'ensure-dev-zone'
    location_id = 'us-east4'

    # Construct the fully qualified location path.
    parent = f"projects/{project_id}/locations/{location_id}"

    # Construct the request body.
    job = {
        "http_target": {'uri':'https://tesla-home-automation-wqdec5ylvq-uc.a.run.app/open', 'http_method': 'GET'},
        "schedule": "* * * * *",
        "time_zone": "America/New_York",
    }

    # Use the client to send the job creation request.
    response = client.create_job(request={"parent": parent, "job": job})

    print("Created job: {}".format(response.name))
    # [END cloud_scheduler_create_job]
    client.update_job('projects/ensure-dev-zone/locations/us-east4/jobs/2626789537856806649', {'http_method': 'POST'})
    return response



#projects/ensure-dev-zone/locations/us-east4/jobs/32661473461610032511"
from google.cloud import scheduler_v1
from google.protobuf import duration_pb2, field_mask_pb2

client = scheduler_v1.CloudSchedulerClient()

job = scheduler_v1.Job()
job.name = 'projects/ensure-dev-zone/locations/us-east4/jobs/32661473461610032511'  #f"projects/{PROJECT_ID}/locations/{DATAFLOW_REGION}/jobs/test"
job.schedule = '* * * * 1'

update_mask = field_mask_pb2.FieldMask(paths=['schedule'])

request = scheduler_v1.UpdateJobRequest(
    job=job,
    update_mask=update_mask
)

response = client.update_job(request=request)
print(response.state)

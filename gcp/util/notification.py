from retry import retry
from gcp.util.logs import logger
from google.cloud import pubsub_v1
from gcp.config import settings


@retry(logger=logger, delay=2, tries=2)
def send_push_notification(message):
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(settings['production']['pub_sub']['chanify']['project'],
                                      settings['production']['pub_sub']['chanify']['topic'])
    data = message.encode("utf-8")
    future = publisher.publish(topic_path, data, origin="python-sample", username="gcp")
    return future.result()


if __name__ == "__main__":
    send_push_notification('testing')

from retry import retry
from twilio.rest import Client
from util.logs import logger
from google.cloud import pubsub_v1
from config import settings


@retry(logger=logger, delay=2, tries=2)
def send_sms(message):
    number=''
REMOVED
REMOVED
    try:
REMOVED
        message = client.messages \
            .create(
                body=message,
                from_='+12056548947',
                to=number
            )
        return message.sid
    except Exception as e:
        logger.error('send_sms: issue with sending sms ' + str(e))


@retry(logger=logger, delay=2, tries=2)
def send_push_notification( message):
    publisher = pubsub_v1.PublisherClient()
    tesla_chanify_notification_topic = publisher.topic_path(settings['production']['pub_sub']
                                                                  ['chanify']['project'],
                                                                  settings['production']['pub_sub']['chanify']['topic'])
    return publisher.publish(tesla_chanify_notification_topic, message.encode("utf-8"))



if __name__ == "__main__":
    send_push_notification( 'testing')

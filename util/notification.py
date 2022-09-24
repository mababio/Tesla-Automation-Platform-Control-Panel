from retry import retry
from twilio.rest import Client
from util.logs import logger
from urllib import request, parse


@retry(logger=logger, delay=2, tries=2)
def send_sms(message):
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
def send_push_notification(message):
REMOVED
    message_json = {'text': message}
    data = parse.urlencode(message_json).encode()
    req = request.Request("https://api.chanify.net/v1/sender/" + token, data=data)
    request.urlopen(req)


if __name__ == "__main__":
    send_push_notification( 'testing')

from retry import retry
from twilio.rest import Client
from util.logs import logger
from urllib import request, parse
from config import settings


@retry(logger=logger, delay=2, tries=2)
def send_sms(message):
    number=''
    account_sid = 'ACee89a17cae64509e882c10346e0b5383'
    auth_token = '2cb6371ce7895e94d3a45fedacb39e6f'
    try:
        client = Client(account_sid, auth_token)
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
    token = settings['production']['key']['chanify']
    message_json = {'text': message}
    data = parse.urlencode(message_json).encode()
    req = request.Request("https://api.chanify.net/v1/sender/" + token, data=data)
    request.urlopen(req)


if __name__ == "__main__":
    send_push_notification( 'testing')

from retry import retry
from twilio.rest import Client
from util.logs import logger


@retry(logger=logger, delay=2, tries=2)
def send_sms(message, number='+19144335805'):
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


if __name__ == "__main__":
    send_sms('+19144335805', 'testing')

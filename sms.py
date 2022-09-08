from twilio.rest import Client


def send_sms(number, message):
    account_sid = 'ACee89a17cae64509e882c10346e0b5383'
    auth_token = '2cb6371ce7895e94d3a45fedacb39e6f'
    client = Client(account_sid, auth_token)

    message = client.messages \
        .create(
        body=message,  # "Join Earth's mightiest heroes. Like Kevin Bacon.",
        from_='+12056548947',
        to=number  # '+19144335805'
    )
    return message.sid

if __name__ == "__main__":
    send_sms('+19144335805','testing')

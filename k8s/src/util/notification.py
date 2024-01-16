"""
Author:     Michael Ababio
Date:       08/08/2022
Project:    Tesla Home Automation
File:       notification.py
Send push notification to chanify
"""

from retry import retry
import redis
from logs import logger


# import sys
# sys.path.append('../')

@retry(logger=logger, delay=2, tries=2)
def send_push_notification(message):
    """
    Send push notification to chanify
    :param message:
    """
    r = redis.Redis(
        host='redis-pub-sub',
        port=6379,
        decode_responses=True
    )
    r.publish('chanify-notification', message)


if __name__ == "__main__":
    send_push_notification('testing')

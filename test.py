import requests

url_myq_garage = "https://us-east4-ensure-dev-zone.cloudfunctions.net/function-trigger-myq"
param = {"state": 'open'}
requests.post(url_myq_garage, json=param).json()
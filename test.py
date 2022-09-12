import asyncio
from aiohttp import ClientSession
import pymyq
import time


latlon = self.getlocation()
lat = latlon['lat']
lon = latlon['lon']
reverse_geocode_result = self.gmaps.reverse_geocode((lat, lon))
for i in reverse_geocode_result:
    if 'Arcuri Court' in i['address_components'][0]['long_name']:
        return True
return False


#import pymongo
#from pymongo.server_api import ServerApi
# import requests
# import time
#
# url_myq_garage = "https://us-east4-ensure-dev-zone.cloudfunctions.net/function-trigger-myq"
# param = {"state": 'cd'}
# start = time.time()
# requests.post(url_myq_garage, json=param).json()
# end = time.time()
# print(end - start)


# import requests
#
#
# url_tesla_prox = "https://us-east4-ensure-dev-zone.cloudfunctions.net/function-tesla-prox"
# lat = 40.669911
# lon = -74.095753
#
# lat = 40.669838
# lon-74.095606
#
# lat = 40.670289
# # lon = -74.096681
# # param_prox = {"lat": lat, "lon": lon}
# print(requests.post(url_tesla_prox, json=param_prox).json())

# client = pymongo.MongoClient("mongodb+srv://mababio:aCyCNd9OcpDCOovX@home-automation.mplvx.mongodb.net/?retryWrites=true&w=majority", server_api=ServerApi('1'))
# collection = client['tesla']['tesla_trigger']
#
# val = collection.find_one()
# print(val['lock'])
#
# myquery = {"_id": "IFTTT_TRIGGER_LOCK"}
# newvalues = { "$set": { "lock": 'true' } }
#
# collection.update_one(myquery, newvalues)
#
# print(collection.find_one()['lock'])












# cred = credentials.ApplicationDefault()
# firebase_admin.initialize_app(cred)
#
# db = firestore.client()  # this connects to our Firestore database
# collection = db.collection('trigger_lock')  # opens 'places' collection
# doc = collection.document('Mm4BLLgEHxtgeZIhi6iu')  # specifies the 'rome' document
#
# print(doc.get().to_dict()['IFTTT_TRIGGER_LOCK'])
#
#
#
#
# gcloud projects add-iam-policy-binding ensure-dev-zone --member="s535976716507-compute@developer.gserviceaccount.com" --role="roles/datastore.user"


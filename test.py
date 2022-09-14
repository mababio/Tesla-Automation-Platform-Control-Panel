import asyncio
import time


async def add(x, y):
    time.sleep(2)
    return x + y


async def add1(x, y):
    return x + y

async def get_results():
    res1 =  add(3, 4)
    res2 = await add1(8, 5)

    print(res1, res2)

asyncio.run(get_results())



# import asyncio
# from aiohttp import ClientSession
# import pymyq
# import time
# from app.tesla import Tesla
# #
# tesla_obj = Tesla()
# print(tesla_obj.set_temp('25'))
# print(tesla_obj.tesla.is_on_home_street())
#
# def tesla_get_location():
#     with teslapy.Tesla('michaelkwasi@gmail.com') as tesla:
#         vehicles = tesla.vehicle_list()
#         vehicles[0].sync_wake_up()
#         professor = vehicles[0]
#         tesla_data_climate = professor.api('VEHICLE_DATA')['response']['climate_state']
#         if not tesla_data_climate['is_climate_on']:
#             professor.command('CLIMATE_ON')
#         professor.command('CHANGE_CLIMATE_TEMPERATURE_SETTING', driver_temp='22.7778', passenger_temp='22.7778')
#
#         return  tesla_data_climate
#     #return str(tuple_latlon)

#print(tesla_get_location())
# latlon = self.getlocation()
# lat = latlon['lat']
# lon = latlon['lon']
# reverse_geocode_result = self.gmaps.reverse_geocode((lat, lon))
# for i in reverse_geocode_result:
#     if 'Arcuri Court' in i['address_components'][0]['long_name']:
#         return True
# return False
#

#import pymongo
#from pymongo.server_api import ServerApi
# import requests
# import time
#
# url_myq_garage = "https://us-east4-ensure-dev-zone.cloudfunctions.net/function-tesla-set-temp"
#
# param = {"temp": '22'}
#
# out = requests.post(url_myq_garage, json=param)
#
# print(out)


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


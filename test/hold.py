# import time
#
# val = 10
# while val != 0:
#     print('mike --->')
#     time.sleep(2)
#     val -= 2
#     if val == 2:
#         print('works')
#         break
# else:
#     print('esle this')


import teslapy

def tesla_frunk():
    with teslapy.Tesla('michaelkwasi@gmail.com') as tesla:
        vehicles = tesla.vehicle_list()
        vehicles[0].sync_wake_up()
        vehicles[0].command('CLIMATE_ON')
        vehicles[0].command('CHANGE_CLIMATE_TEMPERATURE_SETTING', driver_temp=22, passenger_temp=23)
        vehicles[0].command('SET_CLIMATE_KEEPER_MODE', climate_keeper_mode=1)
        vehicles[0].command('REMOTE_SEAT_HEATER_REQUEST', heater=1, level=3)
    return 'Set seat heater on for Kimone'
tesla_frunk()

import json
import os

import requests

from data import ApiConnection

API = os.environ.get('API')

app = ApiConnection()
# data_online = requests.get(url=f'{API}').json()
# print(data_online)
# app.synch_data(API)
# app.add_data('Test', '1', '1' ,'1', '1', '1')
app.update()
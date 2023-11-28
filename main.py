import json
import os

import requests

from data import ApiConnection

API = os.environ.get('API')

app = ApiConnection(API)
# data_online = requests.get(url=f'{API}').json()
# print(data_online)
# app.synch_data(API)
app.add_data('Warzywa na palenie do zapiekanki', 0, 3, 1, 1, 1)
# app.data['list'][0]['taken'] = 1
# app.update_taken()
app.update_all()

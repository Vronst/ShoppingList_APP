import requests
import json


def sorting(thing):
    return thing['zone'], thing['priority']


class ApiConnection:

    def __init__(self):
        with open('data.json', "r") as file:
            self.data = json.load(file)

    # function to add product to data offline
    def add_data(self, name, price, zone, priority, quantity, taken):
        self.data['shop'].append(
                {
                    'name': name,
                    'price': price,
                    'zone': zone,
                    'priority': priority,
                    'quantity': quantity,
                    'taken': taken
                }
        )
        with open('data.json', 'w') as file:
            json.dump(self.data, fp=file, indent=4)

    # getting json data from google sheets deleting current
    def synch_data(self, api):
        data_online = requests.get(url=f'{api}').json()
        with open('data.json', "w") as file:
            json.dump(data_online, fp=file, indent=4)
        self.data = data_online

    def update(self):
        update_data = []
        # gets only data with taken = '1'
        # (to not wipe out progress of another person using same app / sheets)
        for part in self.data['shop']:
            if part['taken'] == '1':
                update_data.append(part)
        # print(update_data)
        # TODO: how to update online and note wipe out data
    # function that will sort our dicts based on zone and then priority

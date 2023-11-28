import requests


def sorting(thing):
    return thing['zone'], thing['priority']


class ApiConnection:

    def __init__(self, api):
        self.data = None
        self.api = api
        self.synch_data()

    # function to add product to data offline
    def add_data(self, name, price, zone, priority, quantity, taken):
        new = {
                    'name': name,
                    'price': price,
                    'zone': zone,
                    'priority': priority,
                    'quantity': quantity,
                    'taken': taken
                }
        # checking name in every index of list to see if there is our new element
        # if not appending to list
        for x in range(len(self.data['list'])):
            if new['name'] != self.data['list'][x]['name']:
                if x == len(self.data['list'])-1:
                    self.data['list'].append(new)
                    with open('data.json', 'w') as file:
                        json.dump(self.data, fp=file, indent=4)
                    requests.post(url=self.api, json=self.data)
            else:
                break

    # getting json data from google sheets deleting current
    def synch_data(self):
        self.data = requests.get(url=f'{self.api}').json()

    def update(self):
        update_data = []
        # gets only data with taken = '1'
        # (to not wipe out progress of another person using same app / sheets)
        for part in self.data['list']:
            if part['taken'] == '1':
                update_data.append(part)
        print(update_data)
        # TODO: how to update online and note wipe out data

    # pushing data online

    # function that will sort our dicts based on zone and then priority

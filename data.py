import requests


# function that will sort our dicts based on zone and then priority
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
            "list": {
                'name': name,
                'price': price,
                'zone': zone,
                'priority': priority,
                'quantity': quantity,
                'taken': taken
            }
        }
        # checking name in every index of list to see if there is our new element
        # if not appending to list
        for x in range(len(self.data['list'])):
            if new['list']['name'] != self.data['list'][x]['name']:
                if x == len(self.data['list']) - 1:
                    # self.data['list'].append(new['list'])
                    msg = requests.post(url=self.api, json=new)
                    self.synch_data()
                    print(msg)
            else:
                break

    # getting json data from google sheets deleting current
    def synch_data(self):
        self.data = requests.get(url=f'{self.api}').json()

    def update_taken(self):
        # gets only data with taken = '1'
        # (to not wipe out progress of another person using same app / sheets)
        for part in self.data['list']:
            if part['taken'] == 1:
                self.update(part)

    def update_all(self):
        for part in self.data['list']:
            self.update(part)

    def update(self, part):
        upd = {"list": {
            'name': part['name'],
            'price': part['price'],
            'zone': part['zone'],
            'priority': part['priority'],
            'quantity': part['quantity'],
            'taken': part['taken']
        }}
        requests.put(url=f'{self.api}/{part["id"]}', json=upd)
    # pushing data online

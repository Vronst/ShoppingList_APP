import json
import requests


# kivy works with UrlRequests so needed edits

# function that will sort our dicts based on zone and then priority
def sorting(thing):
    return thing['zone'], thing['priority']


class ApiConnection:

    def __init__(self, api):
        self.data = None
        self.api = api
        try:
            with open('data.json', 'r') as file:
                self.data = json.load(fp=file)
        except FileNotFoundError:
            self.synch_data()

    def save_it(self) -> None:
        with open("data.json", 'w') as file:
            json.dump(self.data, file, indent=4)

    def load_it(self) -> None:
        with open("data.json", 'r') as file:
            self.data = json.load(file)

    # function to add product to data
    def add_data(self, name: str, price: int, zone: int, priority: int, quantity: int, taken: int) -> None:
        new = {
            "list": {
                'name': name,
                'price': price,
                'zone': zone,
                'priority': priority,
                'quantity': quantity,
                'taken': taken,
                'id': 0
            }
        }
        # checking name in every index of list to see if there is our new element
        # if not appending to list
        for x in range(len(self.data['list'])):
            if new['list']['name'] != self.data['list'][x]['name']:
                if x == len(self.data['list']) - 1:
                    # self.data['list'].append(new['list'])
                    new['list']['id'] = x
                    requests.post(url=self.api, json=new)
                    # or make it only local? but what with id?
                    self.synch_data()
            else:
                break

    # getting json data from google sheets deleting current
    def synch_data(self) -> None:
        self.data = requests.get(url=f'{self.api}').json()
        self.save_it()

    # function to change locally statistics of singular product
    def update_part(self, part):
        pass

    # gets only data with taken = '1'
    def update_taken(self) -> None:
        # (to not wipe out progress of another person using same app / sheets)
        for part in self.data['list']:
            if part['taken'] == 1:
                self.update(part)

    def update_all(self) -> None:
        for part in self.data['list']:
            self.update(part)

    # function that completes update_all() and update taken()
    # its purpose is to update singular part
    def update(self, part: dict) -> None:
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

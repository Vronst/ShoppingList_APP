import os

import certifi
import requests
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.storage.jsonstore import JsonStore
from kivy.uix.boxlayout import BoxLayout
# from data import ApiConnection
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.textinput import TextInput
from kivy.network.urlrequest import UrlRequest
from kivy.uix.togglebutton import ToggleButton

store = JsonStore("data.json")
API = os.environ.get('API')


# root = ApiConnection(API)
# TODO: use priority to sort
# TODO: upload it to base (without overwriting and with

# data_online = requests.get(url=f'{API}').json()
# print(data_online)
# app.synch_data()
# app.add_data('test', 0, 1, 1, 1, 1)
# app.data['list'][0]['taken'] = 1
# app.update_taken()
# app.update_all()
class MyToggleButton(ToggleButton):
    def __init__(self, **kwargs):
        super(MyToggleButton, self).__init__(**kwargs)
        self.text = "Taken" if self.state == "down" else "Not taken"
        # Bind the 'state' property to the 'on_state' method
        self.bind(state=self.on_state)

    def on_state(self, instance, value):
        # Change the text based on the state
        if value == 'normal':
            self.text = "Not Taken"
        else:
            self.text = "Taken"


class Menu(ScreenManager):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.fetch_data)
        self.modified = []  # wil store data for partial upload

    def fetch_data(self, obj=None):
        try:
            keys = store.keys()
            zones = []
            details = {}
            taken = []
            expense = 0
            # getting keys so we can find what we need
            for key in keys:
                # get key and use it to acquire zone
                # print(store.get(key)["data"]["zone"])
                zone_info = store.get(key)["data"]["zone"]
                if zone_info not in zones:
                    zones.append(zone_info)
                    # make place for that zone in dictionary
                    details[zone_info] = []
                details[zone_info].append(store.get(key)["data"])
                # data looks like {"1": [{"name":...., "name"...., ....}]
            # print(details)
            # Posortuj listy w każdym kluczu według priorytetu
            for key in details:
                details[key] = sorted(details[key], key=lambda x: x['priority'])
            zones = sorted(zones)
            for zone in zones:
                label = Label(text="Zone " + str(zone), size_hint=(1, None), height=dp(80))
                self.ids.gridLayout.add_widget(label)

                for detail in details[zone]:
                    # print(detail["taken"])
                    if str(detail['taken']) == "0":
                        expense += int(detail['price'])
                        layout = self.list_point(detail)
                        self.ids.gridLayout.add_widget(layout)
                    else:
                        taken.append(detail)
            label = Label(text="Taken", size_hint=(1, None), height=dp(80))
            self.ids.gridLayout.add_widget(label)
            for detail in taken:
                # print(detail)
                layout = self.list_point(detail)
                self.ids.gridLayout.add_widget(layout)
            self.ids.expense.text = str(expense) + " PLN"

        except Exception as e:
            print(e)

    def go_list(self, obj=None):
        self.transition.direction = "left"
        # TODO: here need to make something to load data
        self.current = 'list'

    def go_list_r(self):
        self.transition.direction = "right"
        self.ids.gridLayout.clear_widgets()
        self.ids.main_layout.clear_widgets()
        self.fetch_data()
        self.current = 'list'

    def go_detail(self, obj=None):
        self.transition.direction = "left"
        self.detail_point(obj)
        # self.ids.detail_screen.add_widget(layout)
        self.current = 'detail'

    def go_main(self):
        self.transition.direction = "right"
        self.current = 'main'

    def go_add(self):
        self.transition.direction = "left"
        self.current = 'add'

    def list_point(self, key):
        layout = BoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=dp(80),
            spacing=dp(10),
            padding=dp(5)
        )
        btn = Button(text=key["name"], on_release=self.go_detail)
        lbl = Label(text="x" + str(key["quantity"]), size_hint=(.3, 1))
        layout.add_widget(btn)
        layout.add_widget(lbl)
        return layout

    def detail_point(self, key):
        # preparing space to collect data from text input
        self.labels = []
        # getting keys so we can find what we need
        keys = store.keys()
        for k in keys:
            x = store.get(k)
            # this is finds what product has been clicked
            if x["data"]["name"] == key.text:
                self.details = x["data"]
                break
        # main_layout = GridLayout(cols=1, size_hint=(1, None), height=dp(200))
        # preparing menu which will allow editing data
        for detail in self.details:
            if detail == "id":
                continue
            layout = BoxLayout(
                orientation='horizontal',
                size_hint=(1, None),
                height=dp(80),
                spacing=dp(10),
                padding=dp(5)
            )

            lbl = Label(text=detail, size_hint=(.3, 1))
            print(detail, self.details[detail])
            if detail == "taken":
                if str(self.details[detail]) == "1":
                    toggle_name = "Taken"
                    state = "down"
                else:
                    toggle_name = "Not taken"
                    state = "normal"
                data = MyToggleButton(text=toggle_name, state=state)
            else:
                data = TextInput(multiline=False, text=str(self.details[detail]))
            layout.add_widget(lbl)
            layout.add_widget(data)
            # main_layout.add_widget(layout)
            self.ids.main_layout.add_widget(layout)
            # collecting data from text inputs to modify storage
            self.labels.append(data)

    def truncate_string(self, str_input, max_length):
        str_end = '...'
        length = len(str_input)
        if length > max_length:
            return str_input[:max_length - len(str_end)] + str_end
        else:
            return str_input

    def synchronise(self):
        self.popup_show(0)
        UrlRequest(url=API,
                   method="GET",
                   on_success=self.load_data,
                   req_headers={"Content-Type": "application/json; charset=utf-8"},
                   ca_file=certifi.where(),
                   verify=True)

    def load_data(self, req_body, result):
        # print(req_body, result, type(result), list(result.keys())[0], sep="\n```````````````````````\n")
        store.clear()
        self.ids.gridLayout.clear_widgets()
        for data in result[list(result.keys())[0]]:
            store.put(key=data["id"], data=data)
        self.popup.dismiss()
        self.fetch_data()

    def popup_show(self, key):
        if key == 0:
            t0, t1, t2 = "Synchronising data...", "Synchronising", False
        else:
            t0, t1, t2 = "Uploaded", "Successfully uploaded", True
        layout = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(5))
        label = Label(text=t0)
        label_empty = Label(text=t1)
        layout.add_widget(label)
        layout.add_widget(label_empty)
        self.popup = Popup(title=t1, size_hint=(.8, .5), content=layout, auto_dismiss=t2)
        self.popup.open()

    def save_data(self, obj=None):
        keys = store.keys()
        key_id = None
        # preparing data to overwrite one record
        data = {
            "name": self.labels[0].text,
            "price": int(self.labels[1].text),
            "zone": int(self.labels[2].text),
            "priority": int(self.labels[3].text),
            "quantity": int(self.labels[4].text),
            "taken": "1" if self.labels[5].text.lower() == "taken" else "0"
        }
        print(data["taken"])
        for key in keys:
            # deleting and updating chosen data
            if store.get(key)["data"]["name"] == self.details["name"]:
                store.delete(key)
                store.put(key=key, data=data)
                key_id = key
                break
        # refreshing list
        self.ids.gridLayout.clear_widgets()
        # so we can upload changes we need to append modified
        self.modified.append(key_id)
        self.fetch_data()

    def add_item(self, *args):
        json_data = {
            "list": {
                'name': str(args[0]),
                'price': int(args[1]),
                'zone': int(args[2]),
                'priority': int(args[3]),
                'quantity': int(args[4]),
                'taken': int(1 if args[5] == "Taken" else 0)
            }}
        requests.post(url=API, json=json_data)
        self.transition.direction = "right"
        self.current = "main"

    def upload_data(self):
        for key in self.modified:
            data = store.get(key)["data"]
            json_data = {
                "list": {
                    'name': str(data["name"]),
                    'price': int(data["price"]),
                    'zone': int(data["zone"]),
                    'priority': int(data["priority"]),
                    'quantity': int(data["quantity"]),
                    'taken': int(data["taken"]),
                    'id': int(key)
                }}
            # UrlRequest(url=API + f"/{key}",
            #            method="PUT",
            #            on_success=self.success,
            #            req_headers={"Content-Type": "application/json; charset=utf-8"},
            #            req_body=json_data,
            #            ca_file=certifi.where(),
            #            verify=True)
            requests.put(API + f"/{key}", json=json_data)  # kivy test work for some reason
        self.popup_show(1)
        self.modified.clear()

    def success(self, req, result):
        print(result)
        self.popup_show(1)

    def start_deleting(self, obj=None):
        main = BoxLayout(orientation="vertical")
        layout = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(5))
        label = Label(text="Are you sure you want to delete?")
        main.add_widget(label)
        btn1 = Button(text="Delete", on_press=self.finish_deleting)
        btn2 = Button(text="Cancel", on_press=self.dismiss_del)
        layout.add_widget(btn1)
        layout.add_widget(btn2)
        main.add_widget(layout)
        self.popup_delete = Popup(title="Deleting", size_hint=(.8, .5), content=main, auto_dismiss=False)
        self.popup_delete.open()

    def dismiss_del(self, obj=None):
        self.popup_delete.dismiss()

    def finish_deleting(self, obj=None):
        keys = store.keys()
        for key in keys:
            # deleting and updating chosen data
            if store.get(key)["data"]["name"] == self.details["name"]:
                store.delete(key)
                requests.delete(url=API + f"/{key}")
                self.ids.gridLayout.clear_widgets()
                self.fetch_data()
                break
        self.popup_delete.dismiss()
        self.go_list_r()


class ShoppingApp(App):
    kv = Builder.load_file("ui.kv")

    def build(self):
        return self.kv


if __name__ == '__main__':
    ShoppingApp().run()

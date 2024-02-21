import os

import certifi
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


class Menu(ScreenManager):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.fetch_data)

    def fetch_data(self, obj=None):
        try:
            keys = store.keys()
            zones = []
            details = {}
            # getting keys so we can find what we need
            for key in keys:
                # get key and use it to acquire zone
                print(store.get(key)["data"]["zone"])
                zone_info = store.get(key)["data"]["zone"]
                if zone_info not in zones:
                    zones.append(zone_info)
                    # make place for that zone in dictionary
                    details[zone_info] = []
                details[zone_info].append(store.get(key)["data"])
            zones = sorted(zones)
            for zone in zones:
                label = Label(text="Zone " + str(zone), size_hint=(1, None), height=dp(80))
                self.ids.gridLayout.add_widget(label)
                for detail in details[zone]:
                    print(detail)
                    layout = self.list_point(detail)
                    self.ids.gridLayout.add_widget(layout)
        except Exception as e:
            print(e)

    def go_list(self, obj=None):
        self.transition.direction = "left"
        # TODO: here need to make something to load data
        self.current = 'list'

    def go_list_r(self):
        self.transition.direction = "right"
        self.ids.detail_screen.clear_widgets()
        self.current = 'list'

    def go_detail(self, obj=None):
        self.transition.direction = "left"
        layout = self.detail_point(obj)
        self.ids.detail_screen.add_widget(layout)
        self.current = 'detail'

    def go_main(self):
        self.transition.direction = "right"
        self.current = 'main'

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
        main_layout = GridLayout(cols=1, size_hint=(1, None))
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
            if detail == "taken":
                if self.details[detail] == 1:
                    toggle_name = "Taken"
                else:
                    toggle_name = "Not taken"
                data = ToggleButton(text=toggle_name)
            else:
                data = TextInput(multiline=False, text=str(self.details[detail]))
            layout.add_widget(lbl)
            layout.add_widget(data)
            main_layout.add_widget(layout)
            # collecting data from text inputs to modify storage
            self.labels.append(data)
        return main_layout

    def truncate_string(self, str_input, max_length):
        str_end = '...'
        length = len(str_input)
        if length > max_length:
            return str_input[:max_length - len(str_end)] + str_end
        else:
            return str_input

    def synchronise(self):
        self.popup_show()
        req = UrlRequest(url=API,
                         method="GET",
                         on_success=self.load_data,
                         req_headers={"Content-Type": "application/json; charset=utf-8"},
                         ca_file=certifi.where(),
                         verify=True)

    def load_data(self, req_body, result):
        print(req_body, result, type(result), list(result.keys())[0], sep="\n```````````````````````\n")
        store.clear()
        self.ids.gridLayout.clear_widgets()
        for data in result[list(result.keys())[0]]:
            store.put(key=data["id"], data=data)
        self.popup.dismiss()
        self.fetch_data()

    def popup_show(self):
        layout = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(5))
        label = Label(text="Synchronising data...")
        label_empty = Label(text="")
        layout.add_widget(label)
        layout.add_widget(label_empty)
        self.popup = Popup(title="Synchronising", size_hint=(.8, .5), content=layout, auto_dismiss=False)
        self.popup.open()

    def save_data(self, obj=None):
        keys = store.keys()
        # preparing data to overwrite one record
        data = {
            "name": self.labels.pop(0).text,
            "price": int(self.labels.pop(0).text),
            "zone": int(self.labels.pop(0).text),
            "priority": int(self.labels.pop(0).text),
            "quantity": int(self.labels.pop(0).text),
            "taken": "1" if self.labels.pop(0).text == "taken" else "0"
        }
        for key in keys:
            # deleting and updating chosen data
            if store.get(key)["data"]["name"] == self.details["name"]:
                store.delete(key)
                store.put(key=key, data=data)
                break
        # refreshing list
        self.ids.gridLayout.clear_widgets()
        self.fetch_data()

    def add_item(self):
        pass


class ShoppingApp(App):
    kv = Builder.load_file("ui.kv")

    def build(self):
        return self.kv


if __name__ == '__main__':
    ShoppingApp().run()

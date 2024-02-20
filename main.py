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
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.textinput import TextInput
from kivy.network.urlrequest import UrlRequest


store = JsonStore("data.json")
API = os.environ.get('API')

# root = ApiConnection(API)


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

    def go_detail(self, obj=None):
        self.transition.direction = "left"
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

    def truncate_string(self, str_input, max_length):
        str_end = '...'
        length = len(str_input)
        if length > max_length:
            return str_input[:max_length - len(str_end)] + str_end
        else:
            return str_input

    def synchronise(self):
        req = UrlRequest(url=API,
                         method="GET",
                         on_success=self.load_data,
                         req_headers={"Content-Type": "application/json; charset=utf-8"},
                         ca_file=certifi.where(),
                         verify=True)

    def load_data(self, req_body, result):
        print(req_body, result, type(result), list(result.keys())[0], sep="\n```````````````````````\n")
        for data in result[list(result.keys())[0]]:
            store.put(key=data["id"], data=data)
        self.fetch_data()

    # def show_popup(self):
        # layout = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(10))
        # btn = Button(text='Submit')
        # btn.bind(on_press=self.add_item)
        # self.text_input = TextInput(multiline=False)
        # layout.add_widget(self.text_input)
        # layout.add_widget(btn)
        # self.popup = Popup(title="Notice title", size_hint=(.8, None), height=dp(180), content=layout)
        # self.popup.open()


class ShoppingApp(App):
    kv = Builder.load_file("ui.kv")

    def build(self):
        return self.kv


if __name__ == '__main__':
    ShoppingApp().run()

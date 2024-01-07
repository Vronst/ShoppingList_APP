import os
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from data import ApiConnection
from kivy.app import App
from kivy.uix.widget import Widget

API = os.environ.get('API')
kv = Builder.load_file("ui.kv")

root = ApiConnection(API)
# data_online = requests.get(url=f'{API}').json()
# print(data_online)
# app.synch_data()
# app.add_data('test', 0, 1, 1, 1, 1)
# app.data['list'][0]['taken'] = 1
# app.update_taken()
# app.update_all()


class Menu(BoxLayout):
    pass


class ShoppingApp(App):
    def build(self):
        return kv

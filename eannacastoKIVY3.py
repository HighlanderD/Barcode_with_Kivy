from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.camera import Camera

Window.clearcolor = (1, 1, 1, 1)
# --------------- do rysowania kodow kreskowych
from barcode import EAN13
from barcode.writer import ImageWriter
import os
import pandas as pd

# -------------------do dekodowania kodow kreskowych
from kivy.clock import Clock
from pyzbar.pyzbar import decode
from PIL import Image

from kivy.utils import platform

if platform == "android":
    from android.permissions import request_permissions, Permission

    DATA_FOLDER = os.getenv('EXTERNAL_STORAGE') or os.path.expanduser("~")
    request_permissions([
        Permission.CAMERA
        # Permission.WRITE_EXTERNAL_STORAGE,
        # Permission.READ_EXTERNAL_STORAGE,
        # Permission.INTERNET,
        # Permission.BODY_SENSORS,
        # Permission.BLUETOOTH
    ])
else:
    print("To nie android")
# --------------------------------------------


ekran = '''
ScreenManager:
    id: screen_manager
    Screen: 
        name: 'ekran 1'
        GridLayout:
            rows:5
            spacing: "10dp"
            padding: "10dp"
            #1
            TextInput:
                id: ean_ID
                hint_text: "Podaj kod EAN"
                font_size: "22dp"
                pos_hint: {'center_x': 0.5, 'center_y': .88}
                size_hint: .8, None
                height: "43dp"
                multiline: False

            #2    
            GridLayout:
                cols: 3
                spacing: "10dp"
                Button:
                    text: "Wyczyść"
                    size_hint_x: None
                    size_hint_y: None
                    height: '48dp'
                    width: '110dp'
                    background_color: 0, 0.5, 0.8, 1
                    background_normal: ""
                    on_press: app.wyczysc()
                    #on_press: app.przechwycobraz()

                Button:
                    id: zamiana_ID 
                    text: "EAN/CASTO"
                    size_hint_x: .8
                    size_hint_y: None
                    height: '48dp'
                    background_color: 0, 0.5, 0.8, 1
                    background_normal: ""
                    on_press: app.tryb() 
                Button:
                    text: "OK"    
                    size_hint_x: None
                    size_hint_y: None
                    height: '48dp'
                    width: '110dp'
                    background_color: 0, 0.5, 0.8, 1
                    background_normal: ""
                    on_press: app.pokaz_ean()



            #3
            BoxLayout:
                id: obraz               
                rows:1 
                size_hint_y: 1
                pos_hint: {'center_x': .5, 'top': 1}
                canvas.before:
                    PushMatrix
                    Rotate:
                        angle: -90
                        origin: self.center
                canvas.after:
                    PopMatrix 

            #4
            Image:
                id: image_ean
                #allow_stretch: True
                size_hint_y: 1    
                source: '1x1.png'

            #5               
            ToggleButton:
                text: 'Skanowanie'
                #on_press: kamera.play = not kamera.play
                on_press:app.wlaczkamere()
                size_hint_y: None
                height: '48dp'
                background_color: 0, 0.5, 0.8, 1
                background_normal: ""


        Label:
            id: label_ID
            text: '' 
            font_style: "H3"                       
            color: 0, 0.5, 0.8, 1      
            pos_hint: {"center_x": .5, "center_y": .78}
            size_hint_x: .5
            size_hint_y: None
            height: "48dp"


'''


class eannacastoKIVY(App):

    def build(self):
        self.cam = Camera(resolution=(640, 480), play=False)
        self.licznik = 0
        self.on_off = False  # wylaczony
        self.jakitryb = 0
        self.ean_list = []
        self.casto_list = []
        self.wyciagnij_z_pliku()
        return Builder.load_string(ekran)

    def wlaczkamere(self):
        if self.licznik > 0:  # nie tworz widgetu wiecej niz 1 raz
            pass
        else:
            self.root.ids.obraz.add_widget(self.cam)
            self.licznik = 1

        self.cam.play = not self.cam.play
        if self.cam.play == True:
            print("Jest wlaczona")
            Clock.schedule_interval(self.przechwycobraz, 1.0 / 15.0)  # przechwytuje klatki
        else:
            print("jest wylaczona")
            self.root.ids.obraz.remove_widget(self.cam)
            Clock.unschedule(self.przechwycobraz)
            self.licznik = 0

    def przechwycobraz(self, *args):
        if self.cam.play == True:
            texture = self.cam.texture  # zamiana Image na obraz mozliwy do dekodowania
            size = texture.size  # aby uniknac zapisu do pliku
            pixels = texture.pixels
            self.frame = Image.frombytes(mode='RGBA', size=size, data=pixels)
            self.dekodowanie()


        else:
            self.mojedane = ""
            pass

    def dekodowanie(self):

        for code in decode(self.frame):
            print(code.data.decode('utf-8'))
            self.mojedane = code.data.decode('utf-8')
            print(self.mojedane)
            if (self.mojedane == ""):
                pass
            else:
                wskaznik = self.root.ids.ean_ID  # jezeli udalo sie zdekodowac to uzupelnij pole zdekodowanym kodem ean
                wskaznik.text = self.mojedane
                #self.cam.play = not self.cam.play  # i wylacz kamere
                self.root.ids.obraz.remove_widget(self.cam)
                self.licznik = 0

    def sprwadzwpisywanie(self, input):
        wskaznik = self.root.ids.ean_ID
        do_sprawdzenia = wskaznik.text
        try:
            wartosc = int(do_sprawdzenia)
            print("Liczba jest intigerem: ", wartosc)
            self.kodbledu = 0
        except ValueError:
            print("wpisz intiger")
            self.kodbledu = 1

    def wyciagnij_z_pliku(self):
        self.nazwa_pliku = "baza_kodow_ean.csv"
        if os.path.exists(self.nazwa_pliku):
            print("jest taki plik")
            self.baza = pd.read_csv(self.nazwa_pliku)
            print("wczytalem baze")
            self.ilosc_wierszy = len(self.baza.index)  # dlugosc bazy
            for i in range(self.ilosc_wierszy):
                self.ean_list.append(self.baza["ean"][i])
                self.casto_list.append(self.baza["casto"][i])

        else:
            print("nie ma takiego pliku")

    def wyczysc(self):
        wskaznik = self.root.ids.ean_ID
        wskaznik.text = ''
        wskaznik2 = self.root.ids.image_ean
        wskaznik2.source = '1x1.png'  # zamiast zdjecia ean dajemy obrazek 1x1 pixel
        wskaznik3 = self.root.ids.label_ID
        wskaznik3.text = ""

    def tryb(self):
        # global on_off
        self.on_off = not self.on_off
        if self.on_off == False:
            self.jakitryb = 0
            print(self.on_off)
            wskaznik = self.root.ids.zamiana_ID
            wskaznik.background_color = (0, 0.5, 0.8, 1)
            wskaznik.background_normal = ""
            wskaznik.text = 'EAN/CASTO'
            wskaznik2 = self.root.ids.ean_ID
            wskaznik2.hint_text = "Podaj kod EAN"
            print("tryb ean>casto", self.jakitryb)
        else:
            self.jakitryb = 1
            print(self.on_off)
            wskaznik = self.root.ids.zamiana_ID
            wskaznik.background_color = "red"
            wskaznik.text = 'CASTO/EAN'
            wskaznik2 = self.root.ids.ean_ID
            wskaznik2.hint_text = "Podaj kod CASTO"
            print("tryb casto>ean", self.jakitryb)

    def pokaz_ean(self):

        wskaznik = self.root.ids.ean_ID
        number = wskaznik.text

        self.sprwadzwpisywanie(number)  # sprawdzanie czy wpisano wartosc intiger
        print("Kod bledu: ", self.kodbledu)

        if self.kodbledu == 1:
            wskaznik3 = self.root.ids.label_ID
            wskaznik3.text = "Musisz wpisać liczbę całkowitą"

        else:
            wskaznik3 = self.root.ids.label_ID
            wskaznik3.text = ""

            if self.jakitryb == 0:  # sprawdzanie bledow dlugosci znakow ean = 13 casto = 6
                self.limitznakow = 13
                print(self.limitznakow)
            else:
                self.limitznakow = 6
                print(self.limitznakow)

            if len(str(number)) != self.limitznakow:
                info = ("Musisz wpisać " + str(self.limitznakow) + " " + "znaków")
                wskaznik3 = self.root.ids.label_ID
                wskaznik3.text = info
            else:
                print("Dlugosc jest ok")

                if self.on_off == False:  # bedziemy wyswietlac ean
                    wskaznik = self.root.ids.label_ID
                    wskaznik.text = ""
                    for i in range(len(self.ean_list)):
                        if self.ean_list[i] == str(number):
                            print("znalazlem w bazie")
                            print("Casto :" + str(self.casto_list[i]))
                            znaleziony = "Casto: " + str(self.casto_list[i])

                            wskaznik.text = znaleziony
                        else:
                            pass

                    my_code = EAN13(number, writer=ImageWriter())
                    my_code.save("new_code1")

                    wskaznik2 = self.root.ids.image_ean
                    wskaznik2.source = 'new_code1.png'
                    wskaznik2.reload()
                    wskaznik = self.root.ids.ean_ID
                    wskaznik.text = ""

                else:  # bedziemy zamieniac ean na casto i wyswietlac
                    wskaznik = self.root.ids.label_ID
                    wskaznik.text = ""
                    for i in range(len(self.casto_list)):
                        if self.casto_list[i] == str(number):
                            print("znalazlem w bazie")
                            print("ean :" + str(self.ean_list[i]))
                            znaleziony = str(self.ean_list[i])
                            wskaznik = self.root.ids.label_ID
                            wskaznik.text = znaleziony

                            my_code = EAN13(znaleziony, writer=ImageWriter())
                            my_code.save("new_code1")

                            wskaznik2 = self.root.ids.image_ean
                            wskaznik2.source = 'new_code1.png'
                            wskaznik2.reload()
                            wskaznik = self.root.ids.ean_ID
                            wskaznik.text = ""

                            break
                        else:
                            pass


if __name__ == "__main__":
    eannacastoKIVY().run()
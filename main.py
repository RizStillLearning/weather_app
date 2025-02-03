# Weather API app
import sys
import requests
import time as tm
import math as m

from geopy.geocoders import OpenCage
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QTimer, QDateTime, QThread, pyqtSignal

weather_api_key = "5f1e14a4a4bcab59a4c3ddbdcad77e42"
opencage_api_key = "2cd24990824d4f46a377d41669bfbd11"

light_theme = True

def get_user_location():
    ipinfo_url = 'https://ipinfo.io/json'
    response = requests.get(ipinfo_url)
    data = response.json()

    if response.status_code != 200:
        return None

    location = data['loc'].split(',')
    return float(location[0]), float(location[1])

def get_country(lat, lon):
    geolocator = OpenCage(api_key=opencage_api_key, timeout=10)  # Increase timeout to 10 seconds
    retries = 3
    for i in range(retries):
        try:
            location = geolocator.reverse((lat, lon), exactly_one=True)
            if location:
                address = location.raw['components']
                country = address.get('country')
                return country
            else:
                return None
        except GeocoderTimedOut:
            if i < retries - 1:  # Retry if not the last attempt
                time.sleep(2)  # Wait for 2 seconds before retrying
                continue
            else:
                raise GeocoderTimedOut("Service timed out after multiple attempts")
        except GeocoderServiceError as e:
            print(f"Geocoding service error: {e}")
            break
    return None

def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(m.radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = m.sin(dlat / 2) ** 2 + m.cos(lat1) * m.cos(lat2) * m.sin(dlon / 2) ** 2
    c = 2 * m.atan2(m.sqrt(a), m.sqrt(1 - a))

    r = 6371.01
    return r * c

def find_closest_city(cities, user_lat, user_lon):
    closest_city = None
    min_distance = float('inf')

    for city in cities:
        lat, lon = city['lat'], city['lon']

        distance = haversine(user_lat, user_lon, lat, lon)
        if distance < min_distance:
            closest_city = city
            min_distance = distance

    return (closest_city, min_distance)

class WeatherFetchThread(QThread):
    data_fetched = pyqtSignal(dict, float)

    def __init__(self, city_name):
        super().__init__()
        self.city_name = city_name

    def run(self):
        base_url = "https://api.openweathermap.org/geo/1.0/direct?"
        params = {
            'q': self.city_name,
            'appid': weather_api_key,
            'limit': 5
        }

        response = requests.get(base_url, params=params)
        distance = 0

        if response.status_code == 200:
            data = response.json()
            if data:
                user_location = get_user_location()
                user_lat = user_location[0]
                user_lon = user_location[1]
                city_info = find_closest_city(data, user_lat, user_lon)
                lat = city_info[0]['lat']
                lon = city_info[0]['lon']
                distance = city_info[1]
                country = get_country(lat, lon)
                weather_data = self.get_weather_data(lat, lon)
                self.data_fetched.emit({
                    'city_info': city_info,
                    'country': country,
                    'weather_data': weather_data
                }, distance)
            else:
                self.data_fetched.emit(None, distance)
        else:
            self.data_fetched.emit(None, distance)

    def get_weather_data(self, lat, lon):
        base_url = "https://api.openweathermap.org/data/2.5/weather?"
        params = {
            'lat': lat,
            'lon': lon,
            'appid': weather_api_key,
            'units': 'metric',
            'lang': 'en'
        }

        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            return response.json()
        return None

class Weather(QWidget):
    def __init__(self):
        super().__init__()
        self.default_stylesheet = None
        self.setWindowTitle("Weather API Application")
        self.setWindowIcon(QIcon("weather.jpg"))

        self.input = QLineEdit(self)

        self.button = QPushButton("Find", self)
        self.theme_button = QPushButton("Change Theme", self)
        self.city_name = QLabel("", self)
        self.distance = QLabel("", self)
        self.temperature = QLabel("", self)
        self.time_label = QLabel("", self)
        self.timer = QTimer(self)

        self.weather_emoji = QLabel("", self)
        self.weather_emoji.setFixedWidth(100)
        self.weather_emoji.setFixedHeight(100)
        self.weather_emoji.setScaledContents(True)

        self.desc = QLabel("", self)
        self.cur_time = QDateTime.currentDateTime()

        self.initUI()

    def initUI(self):
        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setSpacing(0)
        hbox.addWidget(self.input)
        hbox.addWidget(self.button)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addWidget(self.city_name, alignment=Qt.AlignCenter)
        vbox.addWidget(self.distance, alignment=Qt.AlignCenter)
        vbox.addWidget(self.temperature, alignment=Qt.AlignCenter)
        vbox.addWidget(self.weather_emoji, alignment=Qt.AlignCenter)
        vbox.addWidget(self.desc, alignment=Qt.AlignCenter)

        hbox2 = QHBoxLayout()
        hbox2.addWidget(self.time_label, alignment=Qt.AlignLeft)
        hbox2.addWidget(self.theme_button, alignment=Qt.AlignRight)

        vbox.addLayout(hbox2)

        self.setLayout(vbox)

        self.input.setAlignment(Qt.AlignLeft)
        self.city_name.setAlignment(Qt.AlignCenter)
        self.temperature.setAlignment(Qt.AlignCenter)
        self.desc.setAlignment(Qt.AlignCenter)
        self.weather_emoji.setAlignment(Qt.AlignCenter)
        self.time_label.setAlignment(Qt.AlignRight)

        self.button.setObjectName("find")
        self.theme_button.setObjectName("theme_button")
        self.input.setObjectName("input")
        self.weather_emoji.setObjectName("emoji")
        self.time_label.setObjectName("time")

        self.default_stylesheet = """   
            QLabel, QLineEdit, QPushButton {
                font-family: Calibri;
            }
            QLabel {
                font-size: 50px;
            }
            QLineEdit {
                font-size: 30px;
                border-top: 2px solid black;
                border-bottom: 2px solid black;
                border-left: 2px solid black;
                border-top-left-radius: 5px;
                border-bottom-left-radius: 5px;
                padding: 10px;
                width: 700px;
            }
            QLabel#time {
                font-size: 20px;
                padding-top: 10px;
                padding-bottom: 10px;
            }
            QPushButton {
                padding: 10px;
                color: white;
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 black, stop:1 grey);
            }
            QPushButton#theme_button {
                font-size: 30px;
                border: 2px solid black;
                border-radius: 5px;
            }
            QPushButton#find {
                width: 100px;
                font-size: 50px;
                border: 2px solid black;
                border-top-right-radius: 5px;
                border-bottom-right-radius: 5px;
            }
        """

        self.update_time()
        self.setStyleSheet(self.default_stylesheet)

        self.start_clock()
        self.input.setPlaceholderText("Enter a location name")

        self.button.setFixedHeight(self.input.sizeHint().height())

        self.input.returnPressed.connect(self.get_weather_info)
        self.button.clicked.connect(self.get_weather_info)
        self.theme_button.clicked.connect(self.change_theme)

    def start_clock(self):
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

    def update_time(self):
        self.cur_time = QDateTime.currentDateTime()
        self.time_label.setText(self.cur_time.toString(f"hh:mm AP\ndd-MM-yyyy"))

    def change_theme(self):
        global light_theme
        if not light_theme:
            self.setStyleSheet(self.default_stylesheet)
            light_theme = True
        else:
            self.setStyleSheet(self.default_stylesheet + """
                QWidget {
                    background-color: hsl(0, 1%, 10%);
                }
                QLabel {
                    color: white;
                }
                QLineEdit {
                    background-color: hsl(0, 1%, 30%);
                    border-top: 2px solid white;
                    border-bottom: 2px solid white;
                    border-left: 2px solid white;
                    color: white;
                }
                QPushButton#find, QPushButton#theme_button {
                    border: 2px solid white;
                    background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 black, stop:1 grey);
                }
            """)
            light_theme = False

    def get_weather_info(self):
        city_name = self.input.text()
        self.input.setText("")

        self.weather_thread = WeatherFetchThread(city_name)
        self.weather_thread.data_fetched.connect(self.update_ui)
        self.weather_thread.start()

    def update_ui(self, data, distance):
        if data is None:
            self.city_name.setText("City Not Found or Failed to Fetch Data")
            self.reset_label()
            return

        city_info = data['city_info']
        country = data['country']
        weather_data = data['weather_data']
        current_utc_datetime = QDateTime.currentDateTimeUtc()

        if country != city_info[0]['name'] and country is not None:
            self.city_name.setText(f"{city_info[0]['name']}, {country}")
        else:
            self.city_name.setText(f"{city_info[0]['name']}")
        self.distance.setText(f"{distance:.2f} km")

        if weather_data:
            loc_datetime = current_utc_datetime.addSecs(weather_data['timezone'])
            weather_temp = weather_data['main']
            weather_desc = weather_data['weather']

            self.temperature.setText(f"{weather_temp['temp']:.2f}°C")
            self.desc.setText(f"{weather_desc[0]['main']}")

            pixmap = QPixmap()

            if weather_desc[0]['main'] == 'Clouds':
                pixmap = QPixmap("cloud.png")

            elif weather_desc[0]['main'] == 'Rain':
                pixmap = QPixmap("rainy-day.png")

            elif weather_desc[0]['main'] == 'Drizzle':
                pixmap = QPixmap("drizzle.png")

            elif weather_desc[0]['main'] == 'Mist':
                pixmap = QPixmap("mist.png")

            elif weather_desc[0]['main'] == 'Snow':
                pixmap = QPixmap("snow.png")

            elif weather_desc[0]['main'] == 'Clear':
                if 6 <= loc_datetime.time().hour() < 18:
                    pixmap = QPixmap("clear_day.png")
                else:
                    pixmap = QPixmap("clear_night.png")

            elif weather_desc[0]['main'] == 'Haze':
                if 6 <= loc_datetime.time().hour() < 18:
                    pixmap = QPixmap("haze_day.png")
                else:
                    pixmap = QPixmap("haze_night.png")

            elif weather_desc[0]['main'] == 'Thunderstorm':
                pixmap = QPixmap("thunderstorm.png")

            elif weather_desc[0]['main'] == 'Fog':
                pixmap = QPixmap("fog.png")

            self.weather_emoji.setPixmap(pixmap)

    def reset_label(self):
        self.distance.setText("")
        self.temperature.setText("")
        self.desc.setText("")
        self.weather_emoji.setPixmap(QPixmap())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    weather = Weather()
    weather.show()
    sys.exit(app.exec_())
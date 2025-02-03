# Weather API app
import sys
import requests
import time as tm
import math as m

from geopy.geocoders import OpenCage
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QTimer, QDateTime

weather_api_key = "5f1e14a4a4bcab59a4c3ddbdcad77e42"
opencage_api_key = "2cd24990824d4f46a377d41669bfbd11"

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

class Weather(QWidget):
    def __init__(self):
        super().__init__()
        self.default_stylesheet = None
        self.setWindowTitle("Weather API Application")
        self.setWindowIcon(QIcon("weather.jpg"))

        self.input = QLineEdit(self)

        self.button = QPushButton("Find", self)
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
        vbox.addWidget(self.time_label, alignment=Qt.AlignLeft | Qt.AlignBottom)

        self.setLayout(vbox)

        self.input.setAlignment(Qt.AlignLeft)
        self.city_name.setAlignment(Qt.AlignCenter)
        self.temperature.setAlignment(Qt.AlignCenter)
        self.desc.setAlignment(Qt.AlignCenter)
        self.weather_emoji.setAlignment(Qt.AlignCenter)
        self.time_label.setAlignment(Qt.AlignRight)

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
                width: 100px;
                font-size: 50px;
                padding: 10px;
                border: 2px solid black;
                border-top-right-radius: 5px;
                border-bottom-right-radius: 5px;
            }
            QPushButton:hover {
                text-decoration: underline black solid 5px;
            }
        """

        self.update_time()
        self.update_stylesheet()

        self.start_clock()
        self.input.setPlaceholderText("Enter a location name")

        self.button.setFixedHeight(self.input.sizeHint().height())

        self.input.returnPressed.connect(self.get_weather_info)
        self.button.clicked.connect(self.get_weather_info)

    def start_clock(self):
        self.timer.timeout.connect(self.update_time)
        self.timer.timeout.connect(self.update_stylesheet)
        self.timer.start(1000)

    def update_time(self):
        self.cur_time = QDateTime.currentDateTime()
        self.time_label.setText(self.cur_time.toString(f"hh:mm AP\ndd-MM-yyyy"))

    def update_stylesheet(self):
        if 6 <= self.cur_time.time().hour() < 18:
            self.setStyleSheet(self.default_stylesheet)
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
                QPushButton {
                    border: 2px solid white;
                    color: white;
                }
                QPushButton:hover {
                    background-color: hsl(0, 1%, 50%);
                    text-decoration: underline white solid 5px;
                }
            """)

    def get_weather_info(self):
        city_name = self.input.text()
        self.input.setText("")
        current_utc_datetime = QDateTime.currentDateTimeUtc()

        base_url = "https://api.openweathermap.org/geo/1.0/direct?"
        params = {
            'q': city_name,
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
            else:
                self.city_name.setText("City Not Found!")
                self.reset_label()
                return
        else:
            self.city_name.setText("Failed to Fetch Location Data")
            self.reset_label()
            return
        
        country = get_country(lat, lon)
       
        if country is None:
            self.city_name.setText("Country Not Found!")
            self.reset_label()
            return

        if country != city_info[0]['name']:
            self.city_name.setText(f"{city_info[0]['name']}, {country}")
        else:
            self.city_name.setText(f"{city_info[0]['name']}")
        self.distance.setText(f"{distance:.2f} km")

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
            data = response.json()
            if data:
                loc_datetime = current_utc_datetime.addSecs(data['timezone'])
                weather_temp = data['main']
                weather_desc = data['weather']
            else:
                self.temperature.setText("Weather Data Not Found!")
                self.reset_label()
                return
        else:
            self.city_name.setText("Failed to Fetch Weather Data")
            self.reset_label()
            return

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
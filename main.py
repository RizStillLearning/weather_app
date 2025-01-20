# Weather API app
import sys
import requests
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QTimer, QDateTime

api_key = "5f1e14a4a4bcab59a4c3ddbdcad77e42"

class Weather(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Weather API Application")
        self.setWindowIcon(QIcon("weather.jpg"))

        self.input = QLineEdit(self)

        self.button = QPushButton("🔍", self)
        self.city_name = QLabel("", self)
        self.temperature = QLabel("", self)
        self.time_label = QLabel("", self)
        self.timer = QTimer(self)

        self.weather_emoji = QLabel("", self)
        self.weather_emoji.setFixedWidth(70)
        self.weather_emoji.setFixedHeight(70)
        self.weather_emoji.setScaledContents(True)

        self.desc = QLabel("", self)

        self.initUI()

    def initUI(self):
        hbox = QHBoxLayout()
        hbox.addWidget(self.input)
        hbox.addWidget(self.button)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addWidget(self.city_name, alignment=Qt.AlignCenter)
        vbox.addWidget(self.temperature, alignment=Qt.AlignCenter)
        vbox.addWidget(self.weather_emoji, alignment=Qt.AlignCenter)
        vbox.addWidget(self.desc, alignment=Qt.AlignCenter)
        vbox.addWidget(self.time_label, alignment=Qt.AlignLeft)

        self.setLayout(vbox)

        self.input.setAlignment(Qt.AlignLeft)
        self.city_name.setAlignment(Qt.AlignCenter)
        self.temperature.setAlignment(Qt.AlignCenter)
        self.desc.setAlignment(Qt.AlignCenter)
        self.weather_emoji.setAlignment(Qt.AlignCenter)

        self.input.setObjectName("input")
        self.weather_emoji.setObjectName("emoji")
        self.time_label.setObjectName("time")

        self.setStyleSheet("""
            QLabel, QLineEdit, QPushButton {
                font-size: 40px;
                font-family: Calibri;
            }
            QLineEdit#input {
                width: 700px;
            }
            QLabel#time {
                padding-top: 10px;
                padding-bottom: 10px;
            }
            QPushButton {
                font-weight: bold;
            }
            QPushButton:hover {
                text-decoration: underline;
            }
        """)

        self.update_time()
        self.start_clock()
        self.input.setPlaceholderText("Enter a city, region, or country name")
        self.input.returnPressed.connect(self.get_weather_info)
        self.button.clicked.connect(self.get_weather_info)

    def start_clock(self):
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

    def update_time(self):
        cur_time = QDateTime.currentDateTime().toString("HH:mm\ndd-MM-yyyy")
        self.time_label.setText(cur_time)

    def get_weather_info(self):
        city_name = self.input.text()
        self.input.setText("")

        base_url = "https://api.openweathermap.org/geo/1.0/direct?"
        params = {
            'q': city_name,
            'appid': api_key,
            'limit': 1
        }

        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data:
                city_info = data[0]
                lat = city_info['lat']
                lon = city_info['lon']
            else:
                self.city_name.setText("City Not Found!")
                self.reset_label()
                return
        else:
            self.city_name.setText("Failed to fetch location data")
            self.reset_label()
            return

        self.city_name.setText(city_info['name'])

        base_url = "https://api.openweathermap.org/data/2.5/weather?"
        params = {
            'lat': lat,
            'lon': lon,
            'appid': api_key,
            'units': 'metric',
            'lang': 'en'
        }

        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data:
                weather_temp = data['main']
                weather_desc = data['weather']
            else:
                self.temperature.setText("Weather Details Not Found!")
                self.reset_label()
                return
        else:
            self.city_name.setText("Failed to fetch weather data")
            self.reset_label()
            return

        self.temperature.setText(f"{weather_temp['temp']:.2f}°C")
        self.desc.setText(f"{weather_desc[0]['main']}")

        if weather_desc[0]['main'] == 'Clouds':
            pixmap = QPixmap("cloud.png")
            self.weather_emoji.setPixmap(pixmap)
        elif weather_desc[0]['main'] == 'Rain':
            pixmap = QPixmap("rainy-day.png")
            self.weather_emoji.setPixmap(pixmap)
        elif weather_desc[0]['main'] == 'Mist':
            pixmap = QPixmap("mist.png")
            self.weather_emoji.setPixmap(pixmap)
        elif weather_desc[0]['main'] == 'Snow':
            pixmap = QPixmap("snow.png")
            self.weather_emoji.setPixmap(pixmap)
        elif weather_desc[0]['main'] == 'Clear':
            pixmap = QPixmap("clear.png")
            self.weather_emoji.setPixmap(pixmap)
        elif weather_desc[0]['main'] == 'Haze':
            pixmap = QPixmap("haze.png")
            self.weather_emoji.setPixmap(pixmap)
        elif weather_desc[0]['main'] == 'Thunderstorm':
            pixmap = QPixmap("thunderstorm.png")
            self.weather_emoji.setPixmap(pixmap)
        else:
            self.weather_emoji.setPixmap(QPixmap())

    def reset_label(self):
        self.temperature.setText("")
        self.desc.setText("")
        self.weather_emoji.setPixmap(QPixmap())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    weather = Weather()
    weather.show()
    sys.exit(app.exec_())
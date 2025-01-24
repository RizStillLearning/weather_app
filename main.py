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

        self.button = QPushButton("Find", self)
        self.city_name = QLabel("", self)
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
                background-color: lightgray;
                text-decoration: underline black solid 5px;
            }
        """

        self.update_time_stylesheet()
        self.start_clock()
        self.input.setPlaceholderText("Enter a location name")

        self.button.setFixedHeight(self.input.sizeHint().height() + 5)

        self.input.returnPressed.connect(self.get_weather_info)
        self.button.clicked.connect(self.get_weather_info)

    def start_clock(self):
        self.timer.timeout.connect(self.update_time_stylesheet)
        self.timer.start(1000)

    def update_time_stylesheet(self):
        self.cur_time = QDateTime.currentDateTime()

        if 6 <= self.cur_time.time().hour() < 18:
            self.setStyleSheet(self.default_stylesheet)
        else:
            self.setStyleSheet(self.default_stylesheet + """
                QWidget {
                    background-color: hsl(60, 1%, 13%);
                }
                QLabel {
                    color: white;
                }
                QLineEdit {
                    background-color: white;
                    color: black;
                }
                QPushButton {
                    background-color: white;
                    color: black;
                }
            """)
            
        self.time_label.setText(self.cur_time.toString(f"hh:mm AP\ndd-MM-yyyy"))

    def get_weather_info(self):
        city_name = self.input.text()
        self.input.setText("")
        current_utc_datetime = QDateTime.currentDateTimeUtc()

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
            self.city_name.setText("Failed to Fetch Location Data")
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
        self.temperature.setText("")
        self.desc.setText("")
        self.weather_emoji.setPixmap(QPixmap())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    weather = Weather()
    weather.show()
    sys.exit(app.exec_())
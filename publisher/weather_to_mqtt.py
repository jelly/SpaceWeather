#!/usr/bin/python3

import requests
import paho.mqtt.publish as publish

from datetime import datetime


def kelvin_to_celcius(k):
    # Ghetto rounding because I am to lazy to import math
    return int((k - 273.15)*1000)/1000


def publish_weather(prefix, data, forecast=False):
    main = data['main']
    wind = data['wind']
    weather = data['weather'][0]
    clouds = data['clouds']['all']
    try:
        rain = data['rain']['3h']
    except KeyError:
        rain = 0

    msgs = [
            {"topic": prefix + "humidity", "payload": "%s %%" % main['humidity'], "retain": True},
            {"topic": prefix + "pressure", "payload": "%s hPa" % main['pressure'], "retain": True},
            {"topic": prefix + "temperature", "payload": u"%s \xb0C" % kelvin_to_celcius(main['temp']), "retain": True},
            {"topic": prefix + "temperature_min", "payload": u"%s \xb0C" % kelvin_to_celcius(main['temp_min']), "retain": True},
            {"topic": prefix + "temperature_max", "payload": u"%s \xb0C" % kelvin_to_celcius(main['temp_max']), "retain": True},
            {"topic": prefix + "type", "payload": weather['main'], "retain": True},
            {"topic": prefix + "description", "payload": weather['description'], "retain": True},
            # http://openweathermap.org/weather-conditions
            {"topic": prefix + "code", "payload": weather['id'], "retain": True},
            {"topic": prefix + "wind_direction", "payload": u"%s \xb0C" % wind['deg'], "retain": True},
            {"topic": prefix + "wind_speed", "payload": "%s m/s" % wind['speed'], "retain": True},
            {"topic": prefix + "rain", "payload": "%s mm" % rain, "retain": True},
            {"topic": prefix + "clouds", "payload": "%s %%" % clouds, "retain": True},
         ]

    if forecast:  # Unique to normal req
        # Fetch sunset/sunrise
        r = requests.get('http://api.openweathermap.org/data/2.5/weather?id=%s&APPID=%s' % (LOCATION_ID, APPKEY))

        data = r.json()
        # Check if openweathermap failed
        if data['cod'] != 200:
            return

        sys = data['sys']

        sunrise = datetime.fromtimestamp(sys['sunrise'])
        sunset = datetime.fromtimestamp(sys['sunset'])
        msgs.append({"topic": prefix + "sunrise", "payload": sunrise.isoformat(), "retain": True})
        msgs.append({"topic": prefix + "sunset",  "payload":  sunset.isoformat(), "retain": True})

    msgs.append({"topic": prefix + "updated", "payload": datetime.now().isoformat(), "retain": True})

    publish.multiple(msgs, hostname=SERVER)

#  {
#    "id": 6544252,
#    "name": "Gemeente Leidschendam-Voorburg",
#    "country": "NL",
#    "coord": {
#      "lon": 4.40139,
#      "lat": 52.078331
#    }
#  },
LOCATION_ID = '6544252'
APPKEY = ''
SERVER = ''

r = requests.get('http://api.openweathermap.org/data/2.5/forecast?id=%s&APPID=%s' % (LOCATION_ID, APPKEY))
print(r.content)
data = r.json()

# Get the first two hours
for index, data in enumerate(data['list'][0:2]):
    if index == 0:
        prefix = 'revspace/weather/'
        publish_weather(prefix, data)

    if index == 1:
        prefix = 'revspace/weather/forecast/'
        publish_weather(prefix, data, True)

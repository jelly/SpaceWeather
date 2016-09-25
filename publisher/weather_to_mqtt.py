#!/usr/bin/python

import requests
import paho.mqtt.publish as publish

from datetime import datetime

def kelvin_to_celcius(k):
    return k - 273.15

def publish_weather(prefix, data, forecast = False):
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


    if forecast: # Unique to normal req
        # Fetch sunset/sunrise
        r = requests.get('http://api.openweathermap.org/data/2.5/weather?q=%s&APPID=%s' % (CITY, APPKEY))

        data = r.json()
        # Check if openweathermap failed
        if data['cod'] != 200:
            return

        sys = data['sys']

        sunset = datetime.fromtimestamp(sys['sunset'])
        sunrise = datetime.fromtimestamp(sys['sunrise'])
        msgs.append({"topic": prefix + "sunrise", "payload": sunset.isoformat(), "retain": True})
        msgs.append({"topic": prefix + "sunset", "payload": sunrise.isoformat(), "retain": True})

    msgs.append({"topic": prefix + "updated", "payload": datetime.now().isoformat(), "retain": True})

    publish.multiple(msgs, hostname=SERVER)

APPKEY = ''
CITY = 'The Hague'
SERVER = ''

# api.openweathermap.org/data/2.5/forecast?q=London,us&mode=xml
r = requests.get('http://api.openweathermap.org/data/2.5/forecast?q=%s&APPID=%s' % (CITY, APPKEY))
data = r.json()

# Get the first two hours
for index, data in enumerate(data['list'][0:2]):
    if index == 0:
        prefix = 'revspace/weather/'
        publish_weather(prefix, data)

    if index == 1:
        prefix = 'revspace/weather/forecast/'
        publish_weather(prefix, data, True)

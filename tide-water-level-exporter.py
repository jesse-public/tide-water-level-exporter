import os
import requests
import math
import time
from prometheus_client import start_http_server, Gauge
import logging
import threading

logging.basicConfig(
  format="%(asctime)s [%(levelname)-5.5s]  %(message)s",
  level=logging.INFO,
  handlers=[
    logging.StreamHandler()
  ])

stations = [
  {
    "id": 9449880,
    "gauge_id": "water_level_friday_harbor",
    "gauge_name": "Water level: Friday Harbor"
  },
  {
    "id": 9447130,
    "gauge_id": "water_level_seattle",
    "gauge_name": "Water level: Seattle"
  },
  {
    "id": 9446484,
    "gauge_id": "water_level_tacoma",
    "gauge_name": "Water level: Tacoma"
  },
  {
    "id": 9441102,
    "gauge_id": "water_level_westport",
    "gauge_name": "Water level: Westport"
  }
]

DATUM = "MLLW"
URL_TEMPLATE = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?date=latest&station={}&product=water_level&datum={}&time_zone=gmt&units=english&format=json"

MEASURE_INTERVAL = 6 * 60
LISTEN_PORT = 9785

start_http_server(LISTEN_PORT)
logging.info("Started listening on 0.0.0.0:{}".format(LISTEN_PORT))

def poll_station(id, gauge_id, gauge_name):
  water_level = Gauge(gauge_id, gauge_name)

  while True:
    try:
      logging.info("Querying {}...".format(gauge_id))
      resp = requests.get(url=URL_TEMPLATE.format(id, DATUM))
      data = resp.json()["data"][0]
      logging.info("Successfully queried {}! Data: {{ time: {}, height: {} }}".format(gauge_id, data["t"], data["v"]))
    except Exception as e:
      logging.error("Error occured while querying {}.\n{}".format(gauge_id, e))
      data = None

    if data is not None:
      water_level.set(data["v"])

    logging.debug("Querying {} in {}s".format(gauge_id, MEASURE_INTERVAL))
    time.sleep(MEASURE_INTERVAL)

for station in stations:
  thread = threading.Thread(target=poll_station, args=(station["id"], station["gauge_id"], station["gauge_name"]))
  thread.start()

  logging.debug("Querying next station in {}s".format(MEASURE_INTERVAL))
  time.sleep(math.floor(MEASURE_INTERVAL / len(stations)))

import os
import requests
import time
from prometheus_client import start_http_server, Gauge
import logging

logging.basicConfig(
  format="%(asctime)s [%(levelname)-5.5s]  %(message)s",
  level=logging.INFO,
  handlers=[
    logging.StreamHandler()
  ])

STATION_ID = 9447130 # Seattle
DATUM = "MLLW"
URL = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?date=latest&station={}&product=water_level&datum={}&time_zone=gmt&units=english&format=json".format(STATION_ID, DATUM)
MEASURE_INTERVAL = 5 * 60
LISTEN_PORT = 9785

water_level = Gauge("water_level", "Water level")

start_http_server(LISTEN_PORT)
logging.info("Started listening on 0.0.0.0:{}".format(LISTEN_PORT))

while True:
  try:
    resp = requests.get(url=URL)
    data = resp.json()["data"][0]
    logging.info("Acquired data (time: {}, height: {})".format(data["t"], data["v"]))
  except Exception as e:
    logging.error("Error {} occured while getting data.".format(e))
    data = None

  if data is not None:
    water_level.set(data["v"])

  time.sleep(MEASURE_INTERVAL)

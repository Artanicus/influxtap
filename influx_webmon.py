#!/usr/bin/env python3

import yaml
import requests
from influxdb.exceptions import InfluxDBServerError

import time, signal, sys
from absl import flags, logging, app

logging.set_verbosity(logging.WARNING)

def store(results):
    datapoints = []
    for result in results:
        datapoint = {
            'status_code': result.status_code,
            'url': result.request.url,
            'elapsed': result.elapsed,
            'time': int(round(time.time() * 1000))
            }
        print('[{0}] {1} in {2}'.format(datapoint.get('status_code'), datapoint.get('url'), datapoint.get('elapsed')))
        datapoints.append(datapoint)
    print(datapoints)
 #   try:
 #       logging.info('writing to InfluxDB...')
 #       storage.store_sensor_values(datapoint)
 #   except InfluxDBServerError:
 #       logging.warning('Data kept in cache(%s), issues writing to InfluxDB' % (len(results)))
 #   else:
 #       # write succeeded, drop cache
 #       logging.info('write(%s) successful!' % len(sensors))
 #       sensors = []
 #       cache.clear()

def main():
    with open ('example.yaml') as fp:
        config = yaml.load(fp, Loader=yaml.FullLoader)
        results = []
        for url in config.get('urls'):
            results.append(requests.get(url))
        store(results)

# Handle cache dumping if killed.
def sigterm_handler(signal, frame):
    logging.critical('SIGTERM, going down')
    sys.exit(1)

if __name__ == "__main__":
    signal.signal(signal.SIGTERM, sigterm_handler)
    main()


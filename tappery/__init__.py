#!/usr/bin/env python3

import yaml
import requests, datetime
from influxdb import InfluxDBClient, SeriesHelper
from influxdb.exceptions import InfluxDBServerError

from absl import flags, logging

from util import cache

FLAGS = flags.FLAGS


""" Low level InfluxDB series writing helper
"""
class RequestSeries(SeriesHelper):
    class Meta:
        series_name = 'influxtap.request'
        fields = ['status_code', 'elapsed']
        tags = ['url', 'request_type' ]

""" Main class for running the individual requests and storing their results
"""
class Tappery():
    def __init__(self, config):
        self.queue = [] # results queue for storage
        self.cache = cache.Cache() # outgoing write cache handling
        self.reload_config(config)


    """ High-level storage of a list of requests.result objects
    """
    def store(self):
        datapoints = []
        for result in self.queue:
            datapoint = {
                'status_code': result.status_code,
                'request_type': 'GET', # TODO(artanicus): support other request types, perhaps
                'url': result.request.url,
                'elapsed': result.elapsed / datetime.timedelta(milliseconds=1) # store elapsed in milliseconds
                }
            print('[{0}] {1} in {2}'.format(datapoint.get('status_code'), datapoint.get('url'), datapoint.get('elapsed')))
            datapoints.append(datapoint)
        try:
            logging.info('writing to InfluxDB...')
            self._write_influx(datapoints)
        except InfluxDBServerError:
            logging.warning('Data kept in cache(%s), issues writing to InfluxDB' % (len(results)))
        else:
            # write succeeded, drop cache
            logging.info('write(%s) successful!' % len(datapoints))
            self.queue = []
            self.cache.clear()

    """ Do a round of requests and store the results
    """
    def probe(self):
        for url in self.urls:
            self.queue.append(requests.get(url))
        self.store()
    
    """ InfluxDB writer from a list of well formatted datapoints
        - Timestamps are assumed to be in UTC unless overriden with tz
    """
    def _write_influx(self, datapoints):
        for dp in datapoints:
            RequestSeries(**dp)
        RequestSeries.commit(self.db)

    def reload_config(self, config):
        with open(config) as fp:
            config = yaml.load(fp, Loader=yaml.FullLoader)
        self.urls = config.get('urls')
        self.influxdb_config = config.get('influxdb')
        self.db = InfluxDBClient(**self.influxdb_config)

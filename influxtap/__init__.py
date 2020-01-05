#!/usr/bin/env python3

import yaml
import requests, datetime
from influxdb import InfluxDBClient, SeriesHelper
from influxdb.exceptions import InfluxDBServerError
from urllib3.exceptions import NewConnectionError
from requests.exceptions import ConnectionError
from absl import flags, logging

from . import cache

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
        self.requests = [] # results queue for storage
        self.datapoints = [] # queue for datapoints going into storage
        self.cache = cache.Cache() # outgoing write cache handling
        self.reload_config(config)
        if self.cache.exists(): # populate any existing cache dump
            self.datapoints.extend(cache.read())


    """ High-level storage of a list of requests.result objects
    """
    def store(self):
        dps = []
        for result in self.requests:
            dp = {
                'status_code': result.status_code,
                'request_type': 'GET', # TODO(artanicus): support other request types, perhaps
                'url': result.request.url,
                'elapsed': result.elapsed / datetime.timedelta(milliseconds=1) # store elapsed in milliseconds
                }
            logging.info('[{0}] {1} in {2}'.format(result.status_code, result.request.url, result.elapsed))
            dps.append(dp)
        # push to write queue
        self.datapoints.extend(dps)
        # clear read queue
        self.requests = []
        try:
            logging.info('writing to InfluxDB...')
            self._write_influx(self.datapoints)
        except InfluxDBServerError:
            logging.warning('Data kept in cache({0}), issues writing to InfluxDB'.format(len(self.datapoints)))
        else:
            # write succeeded, drop cache
            logging.info('Write({0}) successful!'.format(len(self.datapoints)))
            self.datapoints = [] # clear temporary cache
            self.cache.clear() # clear any permanent cache we may have had

    """ Do a round of requests and store the results
    """
    def probe(self):
        for url in self.urls:
            try:
                self.requests.append(requests.get(url))
            except (ConnectionError, NewConnectionError) as e:
                logging.error('Connection failed [{0}]: {1}'.format(url, e))

    """ InfluxDB writer from a list of well formatted datapoints
        - Timestamps are assumed to be in UTC unless overriden with tz
    """
    def _write_influx(self, datapoints):
        assert(len(datapoints) > 0)
        for dp in datapoints:
            RequestSeries(**dp)
        RequestSeries.commit(self.db)

    def reload_config(self, config):
        with open(config) as fp:
            config = yaml.load(fp, Loader=yaml.FullLoader)
        self.urls = config.get('urls')
        self.influxdb_config = config.get('influxdb')
        self.db = InfluxDBClient(**self.influxdb_config)

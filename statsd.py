'''
Created on Jun 14, 2012

@author: Yangming
'''
import os, sys
_rootpath = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(_rootpath, "..", "statsd_clients", "python"))
sys.path.append(os.path.join(_rootpath, "statsd"))
from afclient import Statsd, AFTransport

BUCKET_PATTERN = "sys.app.%(appname)s.%(type)s"

def set_bucket_pattern(pattern):
    BUCKET_PATTERN = pattern

Statsd.set_transport(AFTransport())

def set_transport(transport):
    Statsd.set_transport(transport)

def timer(method):
    def send_statsd(*args, **kwargs):
        result = method(*args, **kwargs)
        bucket = BUCKET_PATTERN % result
        # TODO: deal with more than one performance data
        if len(result.perf_data_list):
            value = result.perf_data_list[0]['value']
            Statsd.timing(bucket, value, message=result.status)
        return result
    return send_statsd

def counter(method):
    def send_statsd(*args, **kwargs):
        result = method(*args, **kwargs)
        bucket = BUCKET_PATTERN % result
        # TODO: deal with more than one performance data
        if len(result.perf_data_list):
            value = result.perf_data_list[0]['value']
            Statsd.update_stats(bucket, value, 1, result.status)
        return result
    return send_statsd

def gauge(method):
    def send_statsd(*args, **kwargs):
        result = method(*args, **kwargs)
        bucket = BUCKET_PATTERN % result
        # TODO: deal with more than one performance data
        if len(result.perf_data_list):
            value = result.perf_data_list[0]['value']
            Statsd.gauge(bucket, value, message=result.status)
        return result
    return send_statsd

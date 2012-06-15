'''
Created on Jun 14, 2012

@author: appfirst
'''
import os, sys
_rootpath = os.path.dirname(os.path.realpath(__file__))
sys.path.append(
    os.path.join(_rootpath, "..", "statsd_clients", "python"))
from client import Statsd

def timer(bucket, sample_rate=1):
    def make_wrapper(method):
        def wrap_statsd(*args, **kwargs):
            result = method(*args, **kwargs)
            # TODO: deal with more than one performance data
            if len(result.perf_data_list):
                value = result.perf_data_list[0]['value']
                Statsd.timing(bucket, value, sample_rate, result.message)
            return result
        return wrap_statsd
    return make_wrapper

def counter(bucket, sample_rate=1):
    def make_wrapper(method):
        def wrap_statsd(*args, **kwargs):
            result = method(*args, **kwargs)
            # TODO: deal with more than one performance data
            if len(result.perf_data_list):
                value = result.perf_data_list[0]['value']
                Statsd.update_stats(bucket, value, sample_rate, result.message)
            return result
        return wrap_statsd
    return make_wrapper

def gauge(bucket, sample_rate=1):
    def make_wrapper(method):
        def wrap_statsd(*args, **kwargs):
            result = method(*args, **kwargs)
            # TODO: deal with more than one performance data
            if len(result.perf_data_list):
                value = result.perf_data_list[0]['value']
                Statsd.gauge(bucket, value, sample_rate, result.message)
            return result
        return wrap_statsd
    return make_wrapper
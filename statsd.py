'''
Created on Jun 14, 2012

@author: Yangming
'''
import os, sys
_rootpath = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(_rootpath, "..", "statsd_clients", "python"))
sys.path.append(os.path.join(_rootpath, "statsd"))
try:
    from afclient import Statsd, AFTransport
    Statsd.set_transport(AFTransport())
except:
    print "Statsd Library is not available, check PYTHON_PATH"
    Statsd = None

TIMER_BUCKET_PATTERN = "sys.app.%(appname)s.%(name)s"
COUNTER_BUCKET_PATTERN = "sys.app.%(appname)s.%(name)s"
GAUGE_BUCKET_PATTERN = "sys.app.%(appname)s.%(name)s"

def set_timer_bucket_pattern(pattern):
    global TIMER_BUCKET_PATTERN
    TIMER_BUCKET_PATTERN = pattern

def set_counter_bucket_pattern(pattern):
    global COUNTER_BUCKET_PATTERN
    COUNTER_BUCKET_PATTERN = pattern

def set_gauge_bucket_pattern(pattern):
    global GAUGE_BUCKET_PATTERN
    GAUGE_BUCKET_PATTERN = pattern

def timer(method):
    def send_statsd(*args, **kwargs):
        result = method(*args, **kwargs)
        bucket = TIMER_BUCKET_PATTERN % result
        # TODO: deal with more than one performance data
        if len(result.perf_data_list):
            value = result.perf_data_list[0]['value']
            Statsd.timing(bucket, value, message=result.status)
        return result
    if Statsd:
        return send_statsd
    else:
        return method

def counter(method):
    def send_statsd(*args, **kwargs):
        result = method(*args, **kwargs)
        bucket = COUNTER_BUCKET_PATTERN % result
        # TODO: deal with more than one performance data
        if len(result.perf_data_list):
            value = result.perf_data_list[0]['value']
            Statsd.update_stats(bucket, value, 1, result.status)
        return result
    if Statsd:
        return send_statsd
    else:
        return method

def gauge(method):
    def send_statsd(*args, **kwargs):
        result = method(*args, **kwargs)
        bucket = GAUGE_BUCKET_PATTERN % result
        # TODO: deal with more than one performance data
        if len(result.perf_data_list):
            value = result.perf_data_list[0]['value']
            Statsd.gauge(bucket, value, message=result.status)
        return result
    if Statsd:
        return send_statsd
    else:
        return method

if __name__ == "__main__":
    import nagios
    Statsd._transport.verbosity = True
    @timer
    @gauge
    @counter
    def test_wrapper():
        result = nagios.Result("STATSWRAPPER", 0, appname="nagios")
        result.add_performance_data("total", 1)
        return result
    test_wrapper()
'''
Created on May 29, 2012

@author: yangming
@copyright: appfirst inc.
'''
import argparse, sys

class Status(object):
    OK = 0
    WARNING = 1
    CRITICAL = 2
    UNKNOWN = 3

    @staticmethod
    def to_status(status_code):
        if status_code == Status.OK:
            return 'OK'
        elif status_code == Status.WARNING:
            return 'WARNING'
        elif status_code == Status.CRITICAL:
            return 'CRITICAL'
        else:
            return 'UNKNOWN'

class Result(object):
    def __init__(self, service, status_code, message):
        self.service = service.upper()
        self.status_code = status_code
        self.status = Status.to_status(status_code)
        self.message = message
        self.perf_data_list = []

    def add_performance_data(self, label, value, UOM=None,
                             warn=None, crit=None, minv=None, maxv=None):
        perfdata = {'label':label,'value':value,'UOM' :UOM,
                    'warn' :warn, 'crit' :crit, 'minv' :minv, 'maxv' :maxv}
        self.perf_data_list.append(perfdata)
        return self

    def __str__(self):
        output = '{0} {1}: {2}'.format(self.service, self.status, self.message)
        for pd in self.perf_data_list:
            output += self._get_perfdata_output(pd)
        return output

    def _get_perfdata_output(self, perfdata):
        pdline = " | \'{0}\'={1}".format(perfdata["label"], perfdata["value"])
        if perfdata["UOM"] is not None:
            pdline += perfdata["UOM"]
        if perfdata["warn"] is not None:
            pdline += ';%s' % perfdata["warn"]
        if perfdata["crit"] is not None:
            pdline += ';%s' % perfdata["crit"]
        if perfdata["minv"] is not None:
            pdline += ';%s' % perfdata["minv"]
        if perfdata["maxv"] is not None:
            pdline += ';%s' % perfdata["maxv"]
        return pdline

class BaseAnalyst(object):
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self._default_argument()

    def _default_argument(self):
        self.parser.add_argument("-w", "--warn", type=int, required=False)
        self.parser.add_argument("-c", "--crit", type=int, required=False)

    def _parse_range(self, range_str):
        pass

    def run(self):
        self.request = self.parser.parse_args(sys.argv[1:])
        result = self.check(self.request)
        print result
        sys.exit(self.exit_code)

    def check(self, request):
        service = 'service'
        value = 2
        status_code = self.judge(value, request)
        r = Result(service, status_code, 'services %s instances' % value);
        label = 'label'
        UOM = 'c'
        minv = 0
        maxv = 10
        r.add_performance_data(label, value, UOM, request.warn, request.crit, minv, maxv)
        return r

    def judge(self, value, request):
        status_code = Status.UNKNOWN
        if hasattr(request, 'warn') and request.warn is not None and value < request.warn:
            status_code = Status.OK
        elif hasattr(request, 'crit') and request.crit is not None and value >= request.crit:
            status_code = Status.CRITICAL
        elif (hasattr(request, 'warn') and request.warn is not None):
            status_code = Status.WARNING
        else:
            status_code = Status.OK
        return status_code

    @property
    def exit_code(self):
        return 0
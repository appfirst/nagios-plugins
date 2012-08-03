'''
Created on May 29, 2012

@author: Yangming
'''
import argparse, sys, os, pickle
from exceptions import Exception

def BtoMB(bs):
    return bs / (1024 * 1024)

def to_num(v):
    try:
        return int(v)
    except ValueError:
        try:
            return float(v)
        except ValueError:
            return None

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

    @staticmethod
    def to_exit_code(status_code):
        return status_code

class Result(object):
    def __init__(self, appname, type, status_code, message):
        self.appname = appname.lower()
        self.type = type.upper()
        self.status_code = status_code
        self.status = Status.to_status(status_code)
        self.message = message
        self.perf_data_list = []
        self.exit_code = Status.to_exit_code(status_code)

    def add_performance_data(self, label, value, UOM=None,
                             warn=None, crit=None, minv=None, maxv=None):
        perfdata = {'label':label,'value':value,'UOM' :UOM,
                    'warn' :warn, 'crit' :crit, 'minv' :minv, 'maxv' :maxv}
        self.perf_data_list.append(perfdata)
        return self

    def __getitem__(self, key):
        if key == "appname":
            return self.appname
        elif key == "type":
            return self.type.lower()
        elif key == "status_code":
            return self.status_code
        elif key == "status":
            return self.status
        elif key == "message":
            return self.message
        elif key == "value":
            return self.perf_data_list[0]['value']
        else:
            raise KeyError(key)

    def __str__(self):
        output = '%s %s: %s' % (self.type, self.status, self.message)
        if len(self.perf_data_list):
            output += ' |'
        for pd in self.perf_data_list:
            output += self._get_perfdata_output(pd)
        return output

    def _get_perfdata_output(self, perfdata):
        pdline = " %s=%s" % (perfdata["label"], perfdata["value"])
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

class StatusUnknownError(Exception):
    def __init__(self, request, msg=None):
        self.appname = request.appname
        self.status_type = request.type
        self.status = Status.UNKNOWN
        self.msg = msg or "failed to check status. check arguments and try again."

    def __str__(self):
        return str(self.msg)

    @property
    def result(self):
        return Result(self.appname, self.status_type, self.status, str(self))

class MultipleInstancesError(StatusUnknownError):
    def __init__(self, request, msg=None):
        self.status_type = request.type
        self.status = Status.UNKNOWN
        self.msg = msg or "multiple instances found, specific the one you need."

class ServiceInaccessibleError(StatusUnknownError):
    def __init__(self, request, msg=None):
        self.status_type = request.type
        self.status = Status.CRITICAL
        self.msg = msg or "service is not accessible."

class AuthenticationFailedError(StatusUnknownError):
    def __init__(self, request, msg=None):
        self.status_type = request.type
        self.status = Status.UNKNOWN
        self.msg = msg or "authentication failed. please specific user and password"

class OutputFormatError(StatusUnknownError):
    def __init__(self, request, msg=None):
        self.status_type = request.type
        self.status = Status.UNKNOWN
        self.msg = msg or "output format is not as expected."

class BasePlugin(object):
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self._default_argument()

    def _default_argument(self):
        self.parser.add_argument("-w", "--warn", type=int, required=False)
        self.parser.add_argument("-c", "--crit", type=int, required=False)

    def _parse_range(self, range_str):
        pass

    def run(self, args):
        self.request = self.parser.parse_args(args)
        try:
            result = self.check(self.request)
        except StatusUnknownError, e:
            result = e.result
        if result is not None:
            print result
            sys.exit(result.exit_code)
        sys.exit(Status.to_exit_code(Status.UNKNOWN))

    def check(self, request):
        raise NotImplementedError('need to override BasePlugin.check in subclass')

    def verdict(self, value, request):
        # default verdict function
        # ok   if value <  warn             crit
        # warn if          warn <= value <  crit
        # crit if          warn             crit <= value
        # if warn and crit is not defined then it's OK.
        status_code = Status.UNKNOWN
        if request.warn is not None and value < request.warn:
            status_code = Status.OK
        elif request.crit is not None and value >= request.crit:
            status_code = Status.CRITICAL
        elif request.warn is not None:
            status_code = Status.WARNING
        else:
            status_code = Status.OK
        return status_code

class CommandBasedPlugin(BasePlugin):
    def __init__(self, *args, **kwargs):
        super(CommandBasedPlugin, self).__init__(*args, **kwargs)
        if hasattr(self.__class__, "method2commands"):
            method2commands = self.__class__.method2commands
        else:
            method2commands = {}
        self.commands = {}
        for attrname in dir(self):
            obj = getattr(self, attrname)
            if callable(obj) and hasattr(obj,"im_func"):
                method = obj.im_func
                if method in method2commands:
                    command_str = method2commands[method]
                    self.commands[command_str] = method
        self.parser.add_argument("-t", "--type", required=True,
                                 choices=self.commands.keys());

    def check(self, request):
        if request.type in self.commands and self.commands[request.type]:
            result = self.commands[request.type](self, request)
            if result:
                return result
        return Result(request.appname, request.type, Status.UNKNOWN, "mysterious status")

    @classmethod
    def command(cls, command_str, wrappers=None):
        if not hasattr(cls, "method2commands"):
            cls.method2commands = {}
        if wrappers is None:
            wrappers = []
        elif type(wrappers) is not list:
            wrappers = [wrappers]
        def add_command(method):
            for w in wrappers:
                method = w(method)
            cls.method2commands[method] = command_str
            return method
        return add_command

class BatchStatusPlugin(CommandBasedPlugin):
    def __init__(self, *args, **kwargs):
        super(BatchStatusPlugin, self).__init__(*args, **kwargs)
        self.parser.add_argument("-d", "--rootdir", required=False,
                                 default='/tmp/', type=str);

    def retrieve_batch_status(self, request):
        stats = {}
        output = self._get_batch_status(request)
        self._validate_output(request, output)
        stats.update(self._parse_output(request, output))
        if len(stats) == 0:
            raise StatusUnknownError(request, output)
        return stats

    def retrieve_last_status(self, request):
        laststats = {}
        try:
            fn = os.path.join(request.rootdir, request.filename)
            if os.path.exists(fn):
                laststats = pickle.load(open(fn))
        except pickle.PickleError:
            pass
        except EOFError:
            pass
        return laststats

    def save_status(self, request, laststats):
        try:
            fn = os.path.join(request.rootdir, request.filename)
            pickle.dump(laststats, open(fn, "w"))
        except pickle.PickleError:
            pass
        except EOFError:
            pass

    # get the current reading
    def get_status_value(self, attr, request):
        if not hasattr(self, "stats") or self.stats is None:
            self.stats = self.retrieve_batch_status(request)
        if attr not in self.stats:
            raise StatusUnknownError(request)
        else:
            return self.stats[attr]

    # TODO request added, change in all references
    # get changes since last time
    def get_delta_value(self, attr, request):
        value = self.get_status_value(attr, request)
        laststats = self.retrieve_last_status(request)
        if attr in laststats:
            delta = value - laststats[attr]
        else:
            delta = value
        laststats[attr] = value
        self.save_status(request, laststats)
        return delta

    # sub_perfs = [(pfname, pfvalue),...]
    def get_result(self, request, value, message, pfhead="total", UOM=None, sub_perfs=[]):
        status_code = self.verdict(value, request)
        r = Result(request.appname, request.type, status_code, message);
        r.add_performance_data(pfhead, value, UOM=UOM, warn=request.warn, crit=request.crit)
        for pfname, pfvalue in sub_perfs:
            r.add_performance_data(pfname, pfvalue, warn=request.warn, crit=request.crit)
        return r
'''
Created on May 29, 2012

@author: yangming
'''
import argparse, sys
import os, pickle

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
    def __init__(self, service, status_code, message):
        self.service = service.upper()
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

    def __str__(self):
        output = '{0} {1}: {2}'.format(self.service, self.status, self.message)
        if len(self.perf_data_list):
            output += ' |'
        for pd in self.perf_data_list:
            output += self._get_perfdata_output(pd)
        return output

    def _get_perfdata_output(self, perfdata):
        pdline = " {0}={1}".format(perfdata["label"], perfdata["value"])
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
        result = self.check(self.request)
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
        self.parser.add_argument("-t", "--type", required=True,
                                 choices=self.__class__.commandmap.keys());

    def check(self, request):
        if hasattr(self.__class__, "commandmap"):
            commandmap = self.__class__.commandmap
            if request.type in commandmap and commandmap[request.type]:
                result = commandmap[request.type](self, request)
                if result:
                    return result
        return Result(request.type, Status.UNKNOWN, "mysterious status")

    @staticmethod
    def command(command_str, wrappers=None):
        if not hasattr(CommandBasedPlugin, "commandmap"):
            CommandBasedPlugin.commandmap = {}
        if wrappers is None:
            wrappers = []
        elif type(wrappers) is not list:
            wrappers = [wrappers]
        def add_command(method):
            for w in wrappers:
                method = w(method)
            CommandBasedPlugin.commandmap[command_str] = method
            return method
        return add_command

class BatchStatusPlugin(CommandBasedPlugin):
    def __init__(self, *args, **kwargs):
        super(BatchStatusPlugin, self).__init__(*args, **kwargs)
        self.parser.add_argument("-d", "--rootdir", required=False,
                                 default='/tmp/', type=str);

    @staticmethod
    def cumulative(method):
        def cumulative_command(self, request):
            self.stats = self.retrieve_current_status(request)
            if len(self.stats) == 0:
                return Result(request.type, Status.CRITICAL,
                                     "cannot get service status.")
            self.laststats = self.retrieve_last_status(request)
            result = method(self, request)
            self.save_status(request)
            return result
        return cumulative_command

    @staticmethod
    def status(method):
        def status_command(self, request):
            self.stats = self.retrieve_current_status(request)
            if len(self.stats) == 0:
                return Result(request.type, Status.CRITICAL,
                                     "cannot get service status.")
            result = method(self, request)
            return result
        return status_command

    def retrieve_current_status(self, request):
        raise NotImplementedError(
            'need to override BatchStatusPlugin.retrieve_current_status in subclass')

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

    def save_status(self, request):
        try:
            fn = os.path.join(request.rootdir, request.filename)
            pickle.dump(self.laststats, open(fn, "w"))
        except pickle.PickleError:
            pass
        except EOFError:
            pass

    def get_delta_value(self, attr):
        if attr in self.laststats:
            delta = self.stats[attr] - self.laststats[attr]
        else:
            delta = self.stats[attr]
        self.laststats[attr] = self.stats[attr]
        return delta

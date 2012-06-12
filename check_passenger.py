#!/usr/bin/python
'''
Created on Jun 7, 2012

@author: appfirst
'''
import nagios
import commands

class PassengerChecker(nagios.BatchStatusPlugin):
    def __init__(self):
        super(PassengerChecker, self).__init__()
        self.choicemap = {"MAX_PROCESSES"    :self.get_max_procs,
                          "RUNNING_PROCESSES":self.get_procs,
                          "ACTIVE_PROCESSES" :self.get_active_procs}
        self.parser.add_argument("-f", "--filename", required=False, type=str,
                                 default="passenger-status");
        self.parser.add_argument("-t", "--type", required=False, choices=self.choicemap.keys(),
                                 default="RUNNING_PROCESSES");


    def check(self, request):
        self.stats = self.parse_status_output(request)
        if len(self.stats) == 0:
            return nagios.Result(request.type,nagios.Status.CRITICAL,
                                 "cannot connect to passenger.")
        if request.type in self.choicemap and self.choicemap[request.type]:
            return self.choicemap[request.type](request)
        else:
            return nagios.Result(request.type, nagios.Status.UNKNOWN,
                                 "mysterious status")

    def parse_status_output(self, request):
        stats = {}
        cmd = "/usr/bin/passenger-status"
        output = commands.getoutput(cmd)
        if "ERROR" in output:
            return stats
        for l in output.split('\n'):
            pair = l.split('=')
            if len(pair) == 2:
                k = pair[0].strip()
                v = pair[1].strip()
                stats[k] = v
                try:
                    stats[k] = int(v)
                except ValueError:
                    try:
                        stats[k] = float(v)
                    except ValueError:
                        pass
        return stats

    def get_procs(self, request):
        value = self.stats["count"]
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, "%s running processes" % value);
        r.add_performance_data("running_procs", value, warn=request.warn, crit=request.crit)
        return r

    def get_max_procs(self, request):
        value = self.stats["max"]
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, "%s max processes" % value);
        r.add_performance_data("max", value, warn=request.warn, crit=request.crit)
        return r
    def get_active_procs(self, request):
        value = self.stats["active"]
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, "%s active processes" % value);
        r.add_performance_data("active", value, warn=request.warn, crit=request.crit)
        return r

if __name__ == "__main__":
    PassengerChecker().run()
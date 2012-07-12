#!/usr/bin/env python
'''
Created on Jun 22, 2012

@author: Yangming
'''
import datetime
import re
import commands
import nagios
import statsd
from nagios import CommandBasedPlugin as plugin

class MongoDBChecker(nagios.BatchStatusPlugin):
    def __init__(self, *args, **kwargs):
        super(MongoDBChecker, self).__init__(*args, **kwargs)
        self.parser.add_argument("-f", "--filename", default='mongo', type=str, required=False)
        self.parser.add_argument("-u", "--user", required=False, type=str)
        self.parser.add_argument("-s", "--password", required=False, type=str)
        self.parser.add_argument("-H", "--host", required=False, type=str)
        self.parser.add_argument("-p", "--port", required=False, type=int)

    def retrieve_current_status(self, attr, request):
        cmd = "mongostat -n 1 --noheaders"
        output = commands.getoutput(cmd)
        self.validate_output(request, output)
        fields = output.split('\n')[1].strip().split()
        headers = ["insert",     "query",   "update",  "delete",
                   "getmore",    "command", "flushes", "mapped",
                   "vsize",      "res",     "faults",  "locked %",
                   "idx miss %", "qr|qw",   "ar|aw",   "netIn",
                   "netOut",     "conn",    "time"]
        for k, v in zip(headers, fields):
            if k == attr:
                if k == "time":
                    uptime = [int(t) for t in v.split(":")]
                    sec = datetime.timedelta(hours=uptime[0],
                                  minutes=uptime[1],
                                  seconds=uptime[2]).total_seconds()
                    return sec
                elif k == "res":
                    pattern = re.compile('(\d+)m')
                    matchResult = pattern.match(v)
                    value = int(matchResult.groups(1)[0])
                    return value
                else:
                    try:
                        return int(v)
                    except ValueError:
                        try:
                            return float(v)
                        except ValueError:
                            raise nagios.OutputFormatError(request, output)
        raise nagios.StatusUnknownError(request, output)

    @plugin.command("CONNECTIONS")
    @statsd.gauge("sys.app.mongodb.connections")
    def get_connections(self, request):
        cmd = "db.serverStatus().connections.current"
        value = self._single_value_stat(request, cmd)
        if value is None:
            return nagios.Result(request.type,nagios.Status.CRITICAL,
                                "failed to check mongod. check arguments and try again.")
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%s new connections' % value);
        r.add_performance_data('conns', value, warn=request.warn, crit=request.crit)
        return r

    @plugin.command("MEMORY_USED")
    @statsd.gauge("sys.app.mongodb.memory_used")
    def get_memory_used(self, request):
        cmd = "db.serverStatus().mem.resident"
        value = self._single_value_stat(request, cmd)
        if value is None:
            return nagios.Result(request.type,nagios.Status.CRITICAL,
                                "failed to check mongod. check arguments and try again.")
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%sMB resident size' % value);
        r.add_performance_data('res', value, UOM='MB', warn=request.warn, crit=request.crit)
        return r

    @plugin.command("INSERT")
    @statsd.counter("sys.app.mongodb.insert")
    def get_insert(self, request):
        cmd = "db.serverStatus().opcounters.insert"
        value = self._single_value_stat(request, cmd)
        if value is None:
            return nagios.Result(request.type,nagios.Status.CRITICAL,
                                "failed to check mongod. check arguments and try again.")
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%s inserts' % value);
        r.add_performance_data('inserts', value, warn=request.warn, crit=request.crit)
        return r

    @plugin.command("UPDATE")
    @statsd.counter("sys.app.mongodb.update")
    def get_update(self, request):
        cmd = "db.serverStatus().opcounters.update"
        value = self._single_value_stat(request, cmd)
        if value is None:
            return nagios.Result(request.type,nagios.Status.CRITICAL,
                                "failed to check mongod. check arguments and try again.")
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%s updates' % value);
        r.add_performance_data('updates', value, warn=request.warn, crit=request.crit)
        return r

    @plugin.command("COMMAND")
    @statsd.counter("sys.app.mongodb.command")
    def get_command(self, request):
        cmd = "db.serverStatus().opcounters.command"
        value = self._single_value_stat(request, cmd)
        if value is None:
            return nagios.Result(request.type,nagios.Status.CRITICAL,
                                "failed to check mongod. check arguments and try again.")
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%s commands' % value);
        r.add_performance_data('commands', value, warn=request.warn, crit=request.crit)
        return r

    @plugin.command("QUERY")
    @statsd.counter("sys.app.mongodb.query")
    def get_query(self, request):
        cmd = "db.serverStatus().opcounters.query"
        value = self._single_value_stat(request, cmd)
        if value is None:
            return nagios.Result(request.type,nagios.Status.CRITICAL,
                                "failed to check mongod. check arguments and try again.")
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%s queries' % value);
        r.add_performance_data('queries', value, warn=request.warn, crit=request.crit)
        return r

    @plugin.command("DELETE")
    @statsd.counter("sys.app.mongodb.delete")
    def get_delete_rate(self, request):
        cmd = "db.serverStatus().opcounters.delete"
        value = self._single_value_stat(request, cmd)
        if value is None:
            return nagios.Result(request.type,nagios.Status.CRITICAL,
                                "failed to check mongod. check arguments and try again.")
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%s deletes' % value);
        r.add_performance_data('deletes', value, warn=request.warn, crit=request.crit)
        return r

    @plugin.command("LOCKED_PERCENTAGE")
    @statsd.gauge("sys.app.mongodb.locked_ratio")
    def get_locked_ratio(self, request):
        value = self.retrieve_current_status("locked %", request)
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, str(value) + '% locked');
        r.add_performance_data('ratio', value, UOM="%", warn=request.warn, crit=request.crit)
        return r

    @plugin.command("MISS_RATIO")
    @statsd.gauge("sys.app.mongodb.miss_ratio")
    def get_miss_ratio(self, request):
        cmd = "db.serverStatus().indexCounters.btree.missRatio"
        value = self._single_value_stat(request, cmd)
        if value is None:
            return nagios.Result(request.type,nagios.Status.CRITICAL,
                                "failed to check mongod. check arguments and try again.")
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, str(value) + '% missed');
        r.add_performance_data('missed', value, UOM="%", warn=request.warn, crit=request.crit)
        return r

    @plugin.command("RESETS")
    @statsd.counter("sys.app.mongodb.resets")
    def get_resets(self, request):
        cmd = "db.serverStatus().indexCounters.btree.resets"
        value = self._single_value_stat(request, cmd)
        if value is None:
            return nagios.Result(request.type,nagios.Status.CRITICAL,
                                "failed to check mongod. check arguments and try again.")
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, str(value) + '% resets');
        r.add_performance_data('resets', value, UOM="%", warn=request.warn, crit=request.crit)
        return r

    @plugin.command("HITS")
    @statsd.counter("sys.app.mongodb.hits")
    def get_hits(self, request):
        cmd = "db.serverStatus().indexCounters.btree.hits"
        value = self._single_value_stat(request, cmd)
        if value is None:
            return nagios.Result(request.type,nagios.Status.CRITICAL,
                                "failed to check postgres. check arguments and try again.")
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, str(value) + '% hits');
        r.add_performance_data('hits', value, UOM="%", warn=request.warn, crit=request.crit)
        return r

    @plugin.command("MISSES")
    @statsd.counter("sys.app.mongodb.misses")
    def get_misses(self, request):
        cmd = "db.serverStatus().indexCounters.btree.misses"
        value = self._single_value_stat(request, cmd)
        if value is None:
            return nagios.Result(request.type,nagios.Status.CRITICAL,
                                "failed to check postgres. check arguments and try again.")
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, str(value) + '% misses');
        r.add_performance_data('misses', value, UOM="%", warn=request.warn, crit=request.crit)
        return r

    @plugin.command("ACCESSES")
    @statsd.counter("sys.app.mongodb.accesses")
    def get_accesses(self, request):
        cmd = "db.serverStatus().indexCounters.btree.accesses"
        value = self._single_value_stat(request, cmd)
        if value is None:
            return nagios.Result(request.type,nagios.Status.CRITICAL,
                                "failed to check postgres. check arguments and try again.")
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, str(value) + '% accesses');
        r.add_performance_data('accesses', value, UOM="%", warn=request.warn, crit=request.crit)
        return r

    def _single_value_stat(self, request, cmd):
        v = self.run_cmd(cmd, request)
        if v is not None:
            try:
                v = int(v)
            except ValueError:
                try:
                    v = float(v)
                except ValueError:
                    raise nagios.OutputFormatError(request, v)
        return v

    def run_cmd(self, cmd, request):
        cmd_template = "mongo --quiet" 
        if hasattr(request, "user") and request.user is not None:
            cmd_template += " -u %s " % request.user + cmd_template
        if hasattr(request, "password") and request.password is not None:
            cmd_template += " -p %s" % request.password
        if hasattr(request, "host") and request.host is not None:
            cmd_template += " --host %s " % request.host + cmd_template
        if hasattr(request, "port") and request.host is not None:
            cmd_template += " --port %s" % request.port
        cmd_template += " --eval \'%s\'"
        cmd = cmd_template % cmd
        output = commands.getoutput(cmd)
        if self.validate_output(request, output):
            return output

    def validate_output(self, request, output):
        if "command not found" in output:
            raise nagios.ServiceInaccessibleError(request, output)
        elif "Error: couldn't connect to server" in output:
            raise nagios.ServiceInaccessibleError(request, output)
        elif "exception: login failed" in output:
            raise nagios.AuthenticationFailedError(request, output)
        elif "ERROR" in output or output.strip() == "":
            raise nagios.StatusUnknownError(request)
        return True

if __name__ == "__main__":
    import sys
    MongoDBChecker().run(sys.argv[1:])
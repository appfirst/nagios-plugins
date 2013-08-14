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
import argparse

class MongoDBChecker(nagios.BatchStatusPlugin):
    def __init__(self, *args, **kwargs):
        super(MongoDBChecker, self).__init__(*args, **kwargs)
        # Hack to determine uniqueness of script defs
        check = argparse.ArgumentParser()
        check.add_argument("-H", "--host",     required=False, type=str)
        check.add_argument("-p", "--port",     required=False, type=int)
        chk, unknown = check.parse_known_args()

        self.parser.add_argument("-f", "--filename", required=False, type=str, default='pd@mongo')
        self.parser.add_argument("-u", "--user",     required=False, type=str)
        self.parser.add_argument("-s", "--password", required=False, type=str)
        self.parser.add_argument("-H", "--host",     required=False, type=str)
        self.parser.add_argument("-p", "--port",     required=False, type=int)
        self.parser.add_argument("-z", "--appname",  required=False, type=str, default='mongodb')
        self.parser.add_argument("--unique",   required=False, type=str, default=chk.host+str(chk.port))

    def _get_batch_status(self, request):
        cmd = "mongostat -n 1 --noheaders"
        return commands.getoutput(cmd)

    def _parse_output(self, request, output):
        fields = output.split('\n')[1].strip().split()
        headers = ["insert",     "query",   "update",  "delete",
                   "getmore",    "command", "flushes", "mapped",
                   "vsize",      "res",     "faults",  "locked %",
                   "idx miss %", "qr|qw",   "ar|aw",   "netIn",
                   "netOut",     "conn",    "time"]
        for k, v in zip(headers, fields):
            if k == "time":
                uptime = [int(t) for t in v.split(":")]
                if len(uptime) != 3:
                    raise nagios.OutputFormatError(request, output)
                sec = datetime.timedelta(hours=uptime[0],
                                         minutes=uptime[1],
                                         seconds=uptime[2]).total_seconds()
                yield k, sec
            elif "|" in k:
                for k, v in zip(k.split("|"), v.split("|")):
                    value = nagios.to_num(v)
                    if value:
                        yield k, value
            else:
                pattern = re.compile('(\d+)[mkb]?')
                matchResult = pattern.match(v)
                if not matchResult:
                    raise nagios.OutputFormatError(request, output)
                value = int(matchResult.groups(1)[0])
                yield k, value

    def run_query(self, request, query):
        output = self._get_query_status(request, query)
        self._validate_output(request, output)
        return output

    def get_delta_value(self, statkey, request, query):
        output = self.run_query(request, query)
        value = nagios.to_num(output)

        laststats = self.retrieve_last_status(request)
        last_value = laststats.setdefault(statkey, 0)
        laststats[statkey] = value
        self.save_status(request, laststats)

        return value - last_value

    def _get_query_status(self, request, query):
        query_template = "mongo --quiet" 
        if hasattr(request, "user") and request.user is not None:
            query_template += " -u %s " % request.user + query_template
        if hasattr(request, "password") and request.password is not None:
            query_template += " -p %s" % request.password
        if hasattr(request, "host") and request.host is not None:
            query_template += " --host %s " % request.host + query_template
        if hasattr(request, "port") and request.host is not None:
            query_template += " --port %s" % request.port
        query_template += " --eval \'%s\'"
        query = query_template % query
        return commands.getoutput(query)

    def _validate_output(self, request, output):
        if "command not found" in output:
            raise nagios.ServiceInaccessibleError(request, output)
        elif "couldn't connect to server" in output:
            raise nagios.ServiceInaccessibleError(request, output)
        elif "exception: login failed" in output:
            raise nagios.AuthenticationFailedError(request, output)
        elif "ERROR" in output:
            raise nagios.StatusUnknownError(request, output)
        elif output.strip() == "":
            raise nagios.StatusUnknownError(request)
        return True

    @plugin.command("CONNECTIONS")
    @statsd.gauge
    def get_connections(self, request):
        query = "db.serverStatus().connections.current"
        value = nagios.to_num(self.run_query(request, query))
        return self.get_result(request, value, '%s new connections' % value, 'conns')

    @plugin.command("MEMORY_USED")
    @statsd.gauge
    def get_memory_used(self, request):
        query = "db.serverStatus().mem.resident"
        value = nagios.to_num(self.run_query(request, query))
        return self.get_result(request, value, '%sMB resident size' % value, 'res', UOM='MB')

    @plugin.command("INSERT")
    @statsd.gauge
    def get_insert(self, request):
        query = "db.serverStatus().opcounters.insert"
        value = self.get_delta_value("opcounters.insert", request, query)
        return self.get_result(request, value, '%s inserts' % value, 'inserts')

    @plugin.command("UPDATE")
    @statsd.gauge
    def get_update(self, request):
        query = "db.serverStatus().opcounters.update"
        value = self.get_delta_value("opcounters.update", request, query)
        return self.get_result(request, value, '%s updates' % value, 'updates')

    @plugin.command("COMMAND")
    @statsd.gauge
    def get_command(self, request):
        query = "db.serverStatus().opcounters.command"
        value = self.get_delta_value("opcounters.command", request, query)
        return self.get_result(request, value, '%s commands' % value, 'commands')

    @plugin.command("QUERY")
    @statsd.gauge
    def get_query(self, request):
        query = "db.serverStatus().opcounters.query"
        value = self.get_delta_value("opcounters.query", request, query)
        return self.get_result(request, value, '%s queries' % value, 'queries')

    @plugin.command("DELETE")
    @statsd.gauge
    def get_delete_rate(self, request):
        query = "db.serverStatus().opcounters.delete"
        value = self.get_delta_value("opcounters.delete", request, query)
        return self.get_result(request, value, '%s deletes' % value, 'deletes')

    @plugin.command("LOCKED_PERCENTAGE")
    @statsd.gauge
    def get_locked_ratio(self, request):
        value = self.get_status_value("locked %", request)
        return self.get_result(request, value, str(value) + '% locked', 'ratio', UOM="%")

    @plugin.command("MISS_PERCENTAGE")
    @statsd.gauge
    def get_miss_ratio(self, request):
        query = "db.serverStatus().indexCounters.btree.missRatio"
        value = nagios.to_num(self.run_query(request, query))
        return self.get_result(request, value, str(value) + '% missed', 'ratio', UOM="%")

    @plugin.command("RESETS")
    @statsd.gauge
    def get_resets(self, request):
        query = "db.serverStatus().indexCounters.btree.resets"
        value = self.get_delta_value("indexCounters.btree.resets", request, query)
        return self.get_result(request, value, str(value) + 'resets', 'resets')

    @plugin.command("HITS")
    @statsd.gauge
    def get_hits(self, request):
        query = "db.serverStatus().indexCounters.btree.hits"
        value = self.get_delta_value("indexCounters.btree.hits", request, query)
        return self.get_result(request, value, str(value) + 'hits', 'hits')

    @plugin.command("MISSES")
    @statsd.gauge
    def get_misses(self, request):
        query = "db.serverStatus().indexCounters.btree.misses"
        value = self.get_delta_value("indexCounters.btree.misses", request, query)
        return self.get_result(request, value, str(value) + 'misses', 'misses')

    @plugin.command("ACCESSES")
    @statsd.gauge
    def get_accesses(self, request):
        query = "db.serverStatus().indexCounters.btree.accesses"
        value = self.get_delta_value("indexCounters.btree.accesses", request, query)
        return self.get_result(request, value, str(value) + 'accesses', 'accesses')

if __name__ == "__main__":
    import sys
    MongoDBChecker().run(sys.argv[1:])

#!/usr/bin/env python
'''
Created on May 31, 2012

@author: Yangming
'''
import nagios
from nagios import CommandBasedPlugin as plugin
import commands
import statsd

class ResqueChecker(nagios.BatchStatusPlugin):
    def __init__(self, *args, **kwargs):
        super(ResqueChecker, self).__init__(*args, **kwargs)
        self.parser.add_argument("-f", "--filename", required=False, type=str, default='pd@resque_redis-cli')
        self.parser.add_argument("-u", "--user",     required=False, type=str)
        self.parser.add_argument("-s", "--password", required=False, type=str)
        self.parser.add_argument("-H", "--host",     required=False, type=str)
        self.parser.add_argument("-p", "--port",     required=False, type=int)
        self.parser.add_argument("-n", "--database", required=False, type=int)
        self.parser.add_argument("-a", "--appname",  required=False, type=str, default='resque')

    @plugin.command("QUEUE_LENGTH")
    @statsd.gauge
    def get_queue_length(self, request):
        stats = {}
        query = "smembers resque:queues"
        output = self.run_query(request, query)

        total = 0
        status_code = nagios.Status.OK
        query_pattern = "llen resque:queue:%s"
        for q in output.split('\n'):
            if q:
                v = self.run_query(request, query_pattern % q)
                stats[q] = int(v)
                total += stats[q]
                sc = self.verdict(v, request)
                if sc == nagios.Status.WARNING and status_code == nagios.Status.OK:
                    status_code = nagios.Status.WARNING
                elif sc == nagios.Status.CRITICAL:
                    status_code = nagios.Status.CRITICAL

        r = nagios.Result(request.appname, request.type, status_code, '%s jobs in queues' % total);
        r.add_performance_data('total', total, warn=request.warn, crit=request.crit)
        for k, v in stats.iteritems():
            r.add_performance_data(k, v, warn=request.warn, crit=request.crit)
        return r

    @plugin.command("JOB_PROCESSED")
    @statsd.counter
    def get_job_processed(self, request):
        query = "get resque:stat:processed"
        output = self.run_query(request, query)
        if output is None:
            delta = 0
        else:
            value = int(output)
            laststats = self.retrieve_last_status(request)
            delta = value - laststats.setdefault("processed", 0)
            laststats["processed"] = value
            self.save_status(request, laststats)

        return self.get_result(request, value, '%s jobs in processed' % delta)

    def run_query(self, request, query):
        cmd_template = "redis-cli --raw"
        if request.user is not None:
            cmd_template = "sudo -u %s " % request.user + cmd_template
        if request.password is not None:
            cmd_template += " -a %s" % request.password
        if request.database is not None:
            cmd_template += " -n %s" % request.database
        if request.host is not None:
            cmd_template += " -h %s" % request.host
        if request.port is not None:
            cmd_template += " -p %s" % request.port
        cmd = "%s %s" % (cmd_template, query)
        output = commands.getoutput(cmd)
        if "command not found" in output:
            raise nagios.ServiceInaccessibleError(request, output)
        elif output.strip() == "":
            raise nagios.ServiceInaccessibleError(request, output)
        return output

if __name__ == "__main__":
    import sys
    ResqueChecker().run(sys.argv[1:])
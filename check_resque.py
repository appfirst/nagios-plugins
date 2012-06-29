#!/usr/bin/env python
'''
Created on May 31, 2012

@author: yangming
'''
import nagios
from nagios import CommandBasedPlugin as plugin
import commands
import statsd

class ResqueChecker(nagios.BatchStatusPlugin):
    def __init__(self, *args, **kwargs):
        super(ResqueChecker, self).__init__(*args, **kwargs)
        self.parser.add_argument("-f", "--filename", default='resque_redis-cli', type=str, required=False);
        self.parser.add_argument("-u", "--user", required=False, type=str);
        self.parser.add_argument("-a", "--password", required=False, type=str);
        self.parser.add_argument("-H", "--host", required=False, type=str);
        self.parser.add_argument("-p", "--port", required=False, type=str);
        self.parser.add_argument("-n", "--database", required=False, type=int);

    @plugin.command("QUEUE_LENGTH")
    @statsd.gauge("sys.app.resque.queue_length")
    def get_queue_length(self, request):
        stats = {}
        cmd = "smembers resque:queues"
        output = self.run_cmd(cmd, request)

        total = 0
        status_code = nagios.Status.OK
        q_cmd_pattern = "llen resque:queue:%s"
        for q in output.split('\n'):
            if q:
                v = self.run_cmd(q_cmd_pattern % q, request)
                stats[q] = int(v)
                total += stats[q]
                sc = self.verdict(v, request)
                if sc == nagios.Status.WARNING and status_code == nagios.Status.OK:
                    status_code = nagios.Status.WARNING
                elif sc == nagios.Status.CRITICAL:
                    status_code = nagios.Status.CRITICAL

        r = nagios.Result(request.type, status_code, '%s jobs in queues' % total);
        r.add_performance_data('total', total, warn=request.warn, crit=request.crit)
        for k, v in stats.iteritems():
            r.add_performance_data(k, v, warn=request.warn, crit=request.crit)
        return r

    @plugin.command("JOB_PROCESSED")
    @statsd.gauge("sys.app.resque.job_processed")
    def get_job_processed(self, request):
        cmd = "get resque:stat:processed"
        output = self.run_cmd(cmd, request)
        if output is None:
            delta = 0
        else:
            value = int(output)
            self.laststats = self.retrieve_last_status(request)
            delta = value - self.laststats.setdefault("processed", 0)
            self.laststats["processed"] = value
            self.save_status(request)

        status_code = self.verdict(delta, request)
        r = nagios.Result(request.type, status_code, '%s job processed' % delta);
        r.add_performance_data('total', delta, warn=request.warn, crit=request.crit)
        return r

    def run_cmd(self, cmd, request=None):
        cmd_template = "redis-cli --raw"
        if request:
            if hasattr(request, "user") and request.user is not None:
                cmd_template = "sudo -u %s " % request.user + cmd_template
            if hasattr(request, "password") and request.password is not None:
                cmd_template += " -a %s" % request.password
            if hasattr(request, "database") and request.database is not None:
                cmd_template += " -n %s" % request.database
            if hasattr(request, "host") and request.host is not None:
                cmd_template += " -h %s" % request.host
            if hasattr(request, "port") and request.port is not None:
                cmd_template += " -p %s" % request.port
        cmd = "%s %s" % (cmd_template, cmd)
        output = commands.getoutput(cmd)
        if "command not found" in output:
            return None
        elif "FATAL:  role \"root\" does not exist" in output:
            return None
        elif output.strip() == "":
            return None
        return output

if __name__ == "__main__":
    import sys
    ResqueChecker().run(sys.argv[1:])
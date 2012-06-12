#!/usr/bin/python
'''
Created on May 31, 2012

@author: appfirst
'''
import re
import nagios
import commands

class MemcachedChecker(nagios.BatchStatusPlugin):
    def __init__(self):
        super(MemcachedChecker, self).__init__()
        self.choicemap = {"OPERATIONS_SET_REQUESTS":self.get_cmd_set,
                          "OPERATIONS_GET_REQUESTS":self.get_cmd_get,
                          "BYTES_READ"             :self.get_bytes_read,
                          "BYTES_WRITTEN"          :self.get_bytes_written,
                          "BYTES_ALLOCATED"        :self.get_bytes_allocated,
                          "TOTAL_ITEMS"            :self.get_total_items,
                          "TOTAL_CONNECTIONS"      :self.get_total_connections}
        self.parser.add_argument("-f", "--filename", default='memcached_stats', type=str, required=False);
        self.parser.add_argument("-t", "--type", required=True, choices=self.choicemap.keys());
        self.parser.add_argument("-H", "--host", required=False, type=str, default="localhost");
        self.parser.add_argument("-p", "--port", required=False, type=str, default="11211");

    def check(self, request):
        self.stats = self.parse_status_output(request)
        if len(self.stats) == 0:
            return nagios.Result(request.type, nagios.Status.CRITICAL,
                                 "cannot connect to redis.")
        if request.type in self.choicemap and self.choicemap[request.type]:
            return self.choicemap[request.type](request)
        else:
            return nagios.Result(request.type, nagios.Status.UNKNOWN,
                                 "mysterious status")

    def parse_status_output(self, request):
        stats = {}
        cmd = "echo stats | nc"
        cmd += " %s %s" % (request.host, request.port)
        output = commands.getoutput(cmd)
        if "STAT" not in output or "END" not in output:
            return stats
        for l in output.split('\r\n'):
            triple = l.split(" ")
            if triple[0] != "STAT":
                continue
            k = triple[1]
            v = triple[2]
            stats[k] = v
            try:
                stats[k] = int(v)
            except ValueError:
                try:
                    stats[k] = float(v)
                except ValueError:
                    pass
        return stats

    def get_cmd_set(self, request):
        # since last time
        queries = self.get_delta_value("cmd_set")
        sec = self.get_delta_value("uptime")
        value = queries
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%s set requests in %s' % (value, sec));
        r.add_performance_data('set_requests', value, warn=request.warn, crit=request.crit)

        # rate
        value = queries / sec
        r.add_performance_data('set_requests_rate', value, warn=request.warn, crit=request.crit)
        return r

    def get_cmd_get(self, request):
        # since last time
        queries = self.get_delta_value("cmd_get")
        sec = self.get_delta_value("uptime")
        value = queries
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%s get requests in %s' % (value, sec));
        r.add_performance_data('get_requests', value, warn=request.warn, crit=request.crit)

        # rate
        value = queries / sec
        r.add_performance_data('get_requests_rate', value, warn=request.warn, crit=request.crit)
        return r

    def get_bytes_read(self, request):
        # since last time
        total_bytes = self.get_delta_value("bytes_read")
        sec = self.get_delta_value("uptime")
        value = total_bytes
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%s bytes read in %s' % (value, sec));
        r.add_performance_data('bytes_read', value, warn=request.warn, crit=request.crit)

        # rate
        value = total_bytes / sec
        r.add_performance_data('bytes_read_rate', value, warn=request.warn, crit=request.crit)
        return r

    def get_bytes_written(self, request):
        # since last time
        total_bytes = self.get_delta_value("bytes_written")
        sec = self.get_delta_value("uptime")
        value = total_bytes
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%s bytes written in %s' % (value, sec));
        r.add_performance_data('bytes_written', value, warn=request.warn, crit=request.crit)

        # rate
        value = total_bytes / sec
        r.add_performance_data('bytes_written_rate', value, warn=request.warn, crit=request.crit)
        return r

    def get_bytes_allocated(self, request):
        # since last time
        total_bytes = self.get_delta_value("bytes")
        sec = self.get_delta_value("uptime")
        value = total_bytes
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%s bytes allocated in %s' % (value, sec));
        r.add_performance_data('bytes_allocated', value, warn=request.warn, crit=request.crit)

        # rate
        value = total_bytes / sec
        r.add_performance_data('bytes_allocated_rate', value, warn=request.warn, crit=request.crit)
        return r

    def get_total_items(self, request):
        # since last time
        value = self.stats("total_items")
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%s total items' % value);
        r.add_performance_data('items', value, warn=request.warn, crit=request.crit)

    def get_total_connections(self, request):
        # since last time
        value = self.stats("total_connections")
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%s total connections' % value);
        r.add_performance_data('connections', value, warn=request.warn, crit=request.crit)


if __name__ == "__main__":
    MemcachedChecker().run()
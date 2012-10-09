'''
Created on Oct 8, 2012

@author: appfirst
'''
import os
import commands
import nagios
from ping import Ping


class PingPing(Ping):
    '''
    a wrapper class to Ping lib, controlling when to print and some other statistics.
    '''
    def __init__(self, printall=True, *args, **kwargs):
        self.printall = printall
        self.is_started = False
        self.is_unknown_host = False
        self.lost_rate = 0
        self.rta = 0
        super(PingPing, self).__init__(*args, **kwargs)

    def print_start(self):
        self.is_started = True
        if self.printall:
            super(PingPing, self).print_start()

    def print_unknown_host(self, e):
        self.is_unknown_host = True
        if self.printall:
            super(PingPing, self).print_unknown_host()

    def print_success(self, delay, ip, packet_size, ip_header, icmp_header):
        if self.printall:
            super(PingPing, self).print_success(delay, ip, packet_size, ip_header, icmp_header)

    def print_failed(self):
        if self.printall:
            super(PingPing, self).print_failed()

    def print_exit(self):
        lost_count = self.send_count - self.receive_count
        if self.send_count > 0:
            self.lost_rate = float(lost_count) / self.send_count * 100.0
        if self.receive_count > 0:
            self.rta = self.total_time / self.receive_count
        if self.printall:
            super(PingPing, self).print_exit()

class PingChecker(nagios.BasePlugin):
    '''
    classdocs
    '''
    def __init__(self, *args, **kwargs):
        super(PingChecker, self).__init__(*args, **kwargs)
        self.parser.add_argument("-d", "--rootdir",   required=False, type=str,  default='/tmp/');
        self.parser.add_argument("-f", "--filename",  required=False, type=str,  default='pd@ping')
        self.parser.add_argument("-z", "--appname",   required=False, type=str,  default='ping')
        self.parser.add_argument("-H", "--host",      required=True,  type=str,
                                 help="the host to ping")
        self.parser.add_argument("-p", "--path",      required=False, type=str,  default='',
                                 help="path of traceroute")
        self.parser.add_argument("-T", "--timeout",   required=False, type=int,  default=1000,
                                 help="ping timeout, 1 sec by default")
        self.parser.add_argument("-C", "--count",     required=False, type=int,  default=4,
                                 help="the count of pings, by default 4 pings")
        self.parser.add_argument("-P", "--packetsize",required=False, type=int,  default=55,
                                 help="the size of the icmp packet, by default 55 bytes")
        self.parser.add_argument("-m", "--maxttl",    required=False, type=int,  default=8,
                                 help="max ttl/hops of the traceroute, by default 8 hops")
        self.parser.add_argument("-A", "--alloutput", action="store_true",       default=False,
                                 help="the switch to print all the output or just the nagios standard msg")

    def save_output(self, request, output):
        import time, datetime
        start = time.time()
        print "check_traceroute took %s" % (time.time() - start)
        try:
            filename = "%s>%s" % (request.filename, request.host)
            fn = os.path.join(request.rootdir, filename)
            f = open(fn, "w")
            f.write(str(datetime.datetime.now()))
            f.write("\n")
            f.write(output)
            f.write("\n")
            f.close()
        except EOFError:
            pass

    def check_traceroute(self, request):
        cmd = "%straceroute -m %s %s" % (request.path, request.maxttl, request.host)
        cmd = nagios.rootify(cmd)
        output = commands.getoutput(cmd)
        return output

    def check(self, request):
        if os.geteuid() != 0:
            os.seteuid(0)
        p = PingPing(request.alloutput, request.host, request.timeout, request.packetsize)
        if p.is_unknown_host:
            return nagios.Result("PING", nagios.Status.UNKNOWN, "Unknown host: %s" % (request.host), request.appname)
        p.run(request.count)

        # ATTENTION: if nothing receive, it's critical anyway
        if p.receive_count == 0:
            status_code = nagios.Status.CRITICAL
        else:
            status_code = self.verdict(p.lost_rate, request.warn, request.crit)
        msg = "Packet loss = %s %%, RTA = %.3f ms" % (p.lost_rate, p.rta)

        print "traceroute"
        # save traceroute(request, tr_msg)
        if status_code > nagios.Status.OK:
            tr_msg = self.check_traceroute(request)
            self.save_output(request, tr_msg)
            msg += " " + tr_msg
        print "done"

        # generate result
        r = nagios.Result("PING", status_code, msg, request.appname)
        r.add_performance_data("lost_rate", p.lost_rate, UOM="%", warn=request.warn, crit=request.crit)
        r.add_performance_data("rta", p.rta, UOM="ms")
        return r

if __name__ == "__main__":
    import sys
    PingChecker().run(sys.argv[1:])

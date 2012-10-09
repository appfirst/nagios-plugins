'''
Created on Oct 8, 2012

@author: appfirst
'''
import os
import commands
import nagios
from ping import Ping

class PingPing(Ping):
    def __init__(self, printall=True, *args, **kwargs):
        self.printall = printall
        self.start_call_count = False
        self.unknown_host_call_count = False
        self.lost_rate = 0
        self.rta = 0
        super(PingPing, self).__init__(*args, **kwargs)

    def print_start(self):
        self.start_call_count = True
        if self.printall:
            super(PingPing, self).print_start()

    def print_unknown_host(self, e):
        self.unknown_host_call_count = True
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
        self.parser.add_argument("-H", "--host",      required=True,  type=str)
        self.parser.add_argument("-p", "--path",      required=False, type=str,  default='')
        self.parser.add_argument("-T", "--timeout",   required=False, type=int,  default=1000)
        self.parser.add_argument("-C", "--count",     required=False, type=int,  default=4)
        self.parser.add_argument("-P", "--packetsize",required=False, type=int,  default=55)
        self.parser.add_argument("-m", "--maxttl",    required=False, type=int,  default=8)
        self.parser.add_argument("-A", "--alloutput", action="store_true",       default=False)
    
    def save_output(self, request, output):
        import time
        start = time.time()
        print "check_traceroute took %s" % (time.time() - start)
        try:
            filename = "%s->%s" % (request.filename, request.host)
            fn = os.path.join(request.rootdir, filename)
            f = open(fn, "w")
            f.write(output)
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
        if p.unknown_host_call_count:
            return nagios.Result("PING", nagios.Status.UNKNOWN,
                                 "Unknown host: %s" % (request.host), request.appname)
        p.run(request.count)
        if p.send_count == 0:
            status_code = nagios.Status.CRITICAL
        else:
            status_code = self.verdict(p.lost_rate, request.warn, request.crit)

        tr_msg = ""
        if status_code > nagios.Status.OK:
            tr_msg = self.check_traceroute(request)
            self.save_traceroute(request, tr_msg)
        r = nagios.Result("PING", status_code,
            "Packet loss = %s %%, RTA = %.3f ms %s" % (p.lost_rate, p.rta, tr_msg), request.appname)
        
        r.add_performance_data("lost_rate", p.lost_rate, UOM="%", warn=request.warn, crit=request.crit)
        r.add_performance_data("rta", p.rta, UOM="ms")
        return r
    
if __name__ == "__main__":
    import sys
    PingChecker().run(sys.argv[1:])
        
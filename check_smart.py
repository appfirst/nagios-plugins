#!usr/bin/env python
'''
Created on Aug 27, 2012

@author: Yangming
'''
import commands
import nagios
import re
from nagios import CommandBasedPlugin as plugin

class SMARTChecker(nagios.BatchStatusPlugin):
    def __init__(self, *args, **kwargs):
        super(SMARTChecker, self).__init__(*args, **kwargs)
        self.parser.add_argument("-f", "--filename", required=False, type=str, default='pd@smartctl')
        self.parser.add_argument("-z", "--appname",  required=False, type=str, default='smart')
        self.parser.add_argument("-D", "--disk",  required=False, type=str)

    def _get_disks(self, request):
        if request.disk:
            disklist = [request.disk]
        else:
            output = commands.getoutput("sudo /sbin/fdisk -l")
            disklist = re.findall(r"(?<=Disk )((?:/[\w-]+)+)(?=:)", output)
        return disklist

#    def _get_batch_status(self, request):
#        if request.disk:
#            output = commands.getoutput("sudo /sbin/fdisk -l")
#            disks = re.findall(r"(?<=Disk )((?:/[\w-]+)+)(?=:)", output)
#        return commands.getoutput("sudo smartctl -d sat -A %s" % disks[0])

    def _validate_output(self, request, output):
        if "=== START OF READ SMART DATA SECTION ===" in output:
            return True
        elif "Smartctl open device:" in output and "failed: No such device" in output:
            return False
        else:
            raise nagios.StatusUnknownError(request, output)

    def _parse_output(self, request, output):
        metricset = []
        for l in output.split('\n'):
            if "ID#" in l or "Pre-fail" in l or "Old_age" in l:
                fields = l.split()
                if fields[0] == "ID#":
                    metricset = fields
                if fields[0].isdigit() and len(fields) == len(metricset):
                    for metric, value in zip(metricset[2:], fields[2:]):
                        k = "%s.%s" % (fields[0], metric)
                        yield k, value

    def retrieve_batch_status(self, request):
        stats = {}
        for disk in self._get_disks(request):
            output = commands.getoutput("sudo /usr/sbin/smartctl -d sat -A %s" % disk)
            if not self._validate_output(request, output):
                continue
            for k, value in self._parse_output(request, output):
                stats.setdefault(k, {})[disk] = value
        return stats

    def get_status_value(self, attr, request):
        if not hasattr(self, "stats") or self.stats is None:
            self.stats = self.retrieve_batch_status(request)
        if attr not in self.stats:
            raise nagios.StatusUnknownError(request)
        else:
            return self.stats[attr]
        return self.stats[attr];

    @plugin.command("RAW_READ_ERROR_RATE")
    def getRawReadErrorRate(self, request):
        sub_perfs = self.get_status_value("1.VALUE", request)
        thresh = self.get_status_value("1.THRESH", request)
        status_code = nagios.Status.OK
        r = nagios.Result(request.type, status_code, 'raw read error rate', request.appname)
        orig_crit = request.crit
        for disk in sub_perfs:
            request.crit = orig_crit if orig_crit is None else thresh[disk]
            status_code = self.superimpose(status_code, sub_perfs[disk], request, reverse=True)
            r.add_performance_data(disk, sub_perfs[disk], warn=request.warn, crit=request.crit)
        r.set_status_code(status_code)
        return r

    @plugin.command("SPIN_UP_TIME")
    def getSpinUpTime(self, request):
        sub_perfs = self.get_status_value("3.VALUE", request)
        thresh = self.get_status_value("3.THRESH", request)
        status_code = nagios.Status.OK
        r = nagios.Result(request.type, status_code, 'spin up time', request.appname)
        orig_crit = request.crit
        for disk in sub_perfs:
            request.crit = orig_crit if orig_crit is None else thresh[disk]
            status_code = self.superimpose(status_code, sub_perfs[disk], request, reverse=True)
            r.add_performance_data(disk, sub_perfs[disk], warn=request.warn, crit=request.crit)
        r.set_status_code(status_code)
        return r

    @plugin.command("REALLOCATE_SECTOR_COUNT")
    def getReallocatedSectorCt(self, request):
        sub_perfs = self.get_status_value("5.VALUE", request)
        thresh = self.get_status_value("5.THRESH", request)
        status_code = nagios.Status.OK
        r = nagios.Result(request.type, status_code, 'sector reallocation', request.appname)
        orig_crit = request.crit
        for disk in sub_perfs:
            request.crit = orig_crit if orig_crit is None else thresh[disk]
            status_code = self.superimpose(status_code, sub_perfs[disk], request, reverse=True)
            r.add_performance_data(disk, sub_perfs[disk], warn=request.warn, crit=request.crit)
        r.set_status_code(status_code)
        return r

    @plugin.command("SPIN_RETRY_COUNT")
    def getSpinRetryCount(self, request):
        sub_perfs = self.get_status_value("10.VALUE", request)
        thresh = self.get_status_value("10.THRESH", request)
        status_code = nagios.Status.OK
        r = nagios.Result(request.type, status_code, 'spin retries', request.appname)
        orig_crit = request.crit
        for disk in sub_perfs:
            request.crit = orig_crit if orig_crit is None else thresh[disk]
            status_code = self.superimpose(status_code, sub_perfs[disk], request, reverse=True)
            r.add_performance_data(disk, sub_perfs[disk], warn=request.warn, crit=request.crit)
        r.set_status_code(status_code)
        return r

    @plugin.command("REALLOCATED_EVENT_COUNT")
    def getReallocatedEventCount(self, request):
        sub_perfs = self.get_status_value("196.VALUE", request)
        thresh = self.get_status_value("196.THRESH", request)
        status_code = nagios.Status.OK
        r = nagios.Result(request.type, status_code, 'reallocated events', request.appname)
        orig_crit = request.crit
        for disk, in sub_perfs:
            request.crit = orig_crit if orig_crit is None else thresh[disk]
            status_code = self.superimpose(status_code, sub_perfs[disk], request, reverse=True)
            r.add_performance_data(disk, sub_perfs[disk], warn=request.warn, crit=request.crit)
        r.set_status_code(status_code)
        return r

    @plugin.command("CUR_PENDING_SECTOR")
    def getCurrentPendingSector(self, request):
        sub_perfs = self.get_status_value("197.VALUE", request)
        thresh = self.get_status_value("197.THRESH", request)
        status_code = nagios.Status.OK
        r = nagios.Result(request.type, status_code, 'current pending sectors', request.appname);
        orig_crit = request.crit
        for disk in sub_perfs:
            request.crit = orig_crit if orig_crit is None else thresh[disk]
            status_code = self.superimpose(status_code, sub_perfs[disk], request, reverse=True)
            r.add_performance_data(disk, sub_perfs[disk], warn=request.warn, crit=request.crit)
        r.set_status_code(status_code)
        return r

    @plugin.command("OFFLINE_UNCORRECTABLE")
    def getOfflineUncorrectable(self, request):
        sub_perfs = self.get_status_value("198.VALUE", request)
        thresh = self.get_status_value("198.THRESH", request)
        status_code = nagios.Status.OK
        r = nagios.Result(request.type, status_code, 'offline correctability', request.appname)
        orig_crit = request.crit
        for disk, in sub_perfs:
            request.crit = orig_crit if orig_crit is None else thresh[disk]
            status_code = self.superimpose(status_code, sub_perfs[disk], request, reverse=True)
            r.add_performance_data(disk, sub_perfs[disk], warn=request.warn, crit=request.crit)
        r.set_status_code(status_code)
        return r

if __name__ == "__main__":
    import sys
    SMARTChecker().run(sys.argv[1:])

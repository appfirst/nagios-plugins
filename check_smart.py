#!/usr/bin/env python
'''
Created on Aug 27, 2012

@author: Yangming
'''
import commands
import nagios
import re
from xml.dom.minidom import parseString
from nagios import CommandBasedPlugin as plugin

class SMARTChecker(nagios.BatchStatusPlugin):
    def __init__(self, *args, **kwargs):
        super(SMARTChecker, self).__init__(*args, **kwargs)
        self.parser.add_argument("-f", "--filename", required=False, type=str, default='pd@smartctl')
        self.parser.add_argument("-z", "--appname",  required=False, type=str, default='smart')
        self.parser.add_argument("-D", "--disk",     required=False, type=str)
        self.parser.add_argument("-r", "--raid",     required=False, type=str, choices=["adaptec"])

    def _get_disks(self, request):
        if request.disk:
            disklist = [request.disk]
        else:
            cmd = nagios.rootify("/sbin/fdisk -l")
            output = commands.getoutput(cmd)
            disklist = re.findall(r"(?<=Disk )((?:/[\w-]+)+)(?=:)", output)
        return disklist

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
                        attr = "%s.%s" % (fields[0], metric)
                        yield attr, value

    def _map_disknum(self, disklist):
        cmd = nagios.rootify("/usr/StorMan/arcconf getconfig 1")
        output = commands.getoutput(cmd)
        results = re.findall(r"Logical device number(?:.*\n)+?\n", output, re.M)
        diskdict = {}
        for (disk, result) in zip(disklist, results):
            for diskid in re.findall(r"Present \(Controller:\d+,Connector:\d+,Device:(\d+)\)", result, re.M):
                diskdict[diskid] = "%s-%s" % (disk, diskid)

    def _detect_adaptec(self, disklist):
        adaptec_disks = set()
        for disk in disklist:
            cmd = nagios.rootify("sudo /usr/sbin/smartctl -a %s" % disk)
            output = commands.getoutput(cmd)
            if re.search(r"Device: Adaptec\s+(\S+)", output):
                adaptec_disks.add(disk)
        return adaptec_disks;

    def retrieve_batch_status(self, request):
        stats = {}
        disklist = self._get_disks(request)
        if request.raid == "adaptec":
            adaptec_disks = self._detect_adaptec(disklist)
            disklist = filter(lambda d:d not in adaptec_disks, disklist)
            stats.update(self._get_adaptec_status(request, list(adaptec_disks)))
        for disk in disklist:
            cmd = nagios.rootify("/usr/sbin/smartctl -d sat -A %s" % disk)
            output = commands.getoutput(cmd)
            if not self._validate_output(request, output):
                continue
            for attr, value in self._parse_output(request, output):
                stats.setdefault(attr, {})[disk] = value
        return stats

    def _get_adaptec_status(self, request, disklist):
        diskmap = self._map_disknum(disklist)
        stats = {}
        cmd = nagios.rootify("/usr/StorMan/arcconf getsmartstats 1")
        output = commands.getoutput(cmd)
        xml = output[output.index("<SmartStats"):output.index("</SmartStats>")+13]
        dom = parseString(xml)
        for disknode in dom.getElementsByTagName("PhysicalDriveSmartStats"):
            disk = diskmap[disknode.getAttribute("id")]
            for attrnode in disknode.getElementsByTagName("Attribute"):
                attrid = str(int(attrnode.getAttribute("id"), 16))
                stats.setdefault(attrid + ".VALUE", {})[disk] = attrnode.getAttribute("normalizedCurrent")
                stats.setdefault(attrid + ".THRESH", {})[disk] = attrnode.getAttribute("normalizedWorst")
                stats.setdefault(attrid + ".RAW_VALUE", {})[disk] = attrnode.getAttribute("rawValue")
        return stats

    def get_status_value(self, attr, request):
        if not hasattr(self, "stats") or self.stats is None:
            self.stats = self.retrieve_batch_status(request)
        if attr not in self.stats:
            raise nagios.StatusUnknownError(request)
        else:
            return self.stats[attr]
        return self.stats[attr];

    @plugin.command("OVERALL_HEALTH")
    def getOverallHealth(self, request):
        message = "overall test results"
        status_code = nagios.Status.OK
        for disk in self._get_disks(request):
            cmd = nagios.rootify("/usr/sbin/smartctl -d sat -H %s" % disk)
            output = commands.getoutput(cmd)
            if not self._validate_output(request, output):
                continue
            test_result = re.findall(r"(?<=SMART overall-health self-assessment test result: )(\w+)\n", output)[0]
            message += " %s=%s" % (disk, test_result)
            if "PASSED" != test_result:
                status_code = nagios.Status.CRITICAL
        r = nagios.Result(request.type, status_code, message, request.appname)
        return r

    @plugin.command("RAW_READ_ERROR_RATE")
    def getRawReadErrorRate(self, request):
        sub_perfs = self.get_status_value("1.VALUE", request)
        thresh = self.get_status_value("1.THRESH", request)
        status_code = nagios.Status.OK
        r = nagios.Result(request.type, status_code, 'raw read error rate', request.appname)
        orig_crit = request.crit
        for disk in sub_perfs:
            if orig_crit:
                request.crit = orig_crit
            else:
                request.crit = thresh[disk]
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
            if orig_crit:
                request.crit = orig_crit
            else:
                request.crit = thresh[disk]
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
            if orig_crit:
                request.crit = orig_crit
            else:
                request.crit = thresh[disk]
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
            if orig_crit:
                request.crit = orig_crit
            else:
                request.crit = thresh[disk]
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
        for disk in sub_perfs:
            if orig_crit:
                request.crit = orig_crit
            else:
                request.crit = thresh[disk]
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
            if orig_crit:
                request.crit = orig_crit
            else:
                request.crit = thresh[disk]
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
        for disk in sub_perfs:
            if orig_crit:
                request.crit = orig_crit
            else:
                request.crit = thresh[disk]
            status_code = self.superimpose(status_code, sub_perfs[disk], request, reverse=True)
            r.add_performance_data(disk, sub_perfs[disk], warn=request.warn, crit=request.crit)
        r.set_status_code(status_code)
        return r

if __name__ == "__main__":
    import sys
    SMARTChecker().run(sys.argv[1:])

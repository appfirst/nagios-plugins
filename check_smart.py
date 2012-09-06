#!/usr/bin/env python
'''
Created on Aug 27, 2012

@author: Yangming
'''
import commands
import nagios
import re
import time
from xml.dom.minidom import parseString
from nagios import CommandBasedPlugin as plugin

class SMARTChecker(nagios.BatchStatusPlugin):
    def __init__(self, *args, **kwargs):
        super(SMARTChecker, self).__init__(*args, **kwargs)
        self.parser.add_argument("-f", "--filename", required=False, type=str, default='pd@smartctl')
        self.parser.add_argument("-z", "--appname",  required=False, type=str, default='smart')
        self.parser.add_argument("-D", "--disk",     required=False, type=str)
        self.parser.add_argument("-r", "--raid",     required=False, type=str, choices=["adaptec"])
        #the interval (by sec) indicates how often this program will fetch smart info
        #if queried more frequently, it returns merely the last fetched info
        self.parser.add_argument("-i", "--interval", required=False, type=int, default=300)

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

    def _detect_adaptec(self, disklist):
        # map disk name to disk mount path
        adaptec_disks = {}
        diskset = set(disklist)
        for disk in diskset:
            cmd = nagios.rootify("/usr/sbin/smartctl -a %s" % disk)
            output = commands.getoutput(cmd)
            results = re.findall(r"Device: Adaptec\s+(\S+)", output)
            if len(results) == 1:
                adaptec_disks[results[0]] = disk
                disklist.remove(disk)

        # map to disknum to disk name (with disknum)
        cmd = nagios.rootify("/usr/StorMan/arcconf getconfig 1")
        output = commands.getoutput(cmd)
        results = re.findall(r"Logical device number(?:.*\n)+?\n", output, re.M)
        diskdict = {}
        for result in results:
            name = re.findall(r"Logical device name\s*:\s*(.*)", result)[0]
            for diskid in re.findall(r"Present \(\D*\d+,[^)]*?(\d+)\)", result):
                diskdict[diskid] = "%s-%s" % (adaptec_disks[name], diskid)

        return diskdict;

    def retrieve_batch_status(self, request):
        stats = {}
        disklist = self._get_disks(request)

        # load the SMART info of adaptec raid controller
        if request.raid == "adaptec":
            adaptec_diskdict = self._detect_adaptec(disklist)
            if adaptec_diskdict:
                stats.update(self._get_adaptec_status(request, adaptec_diskdict))

        # load the SMART info of the rest disks.
        for disk in disklist:
            cmd = nagios.rootify("/usr/sbin/smartctl -d sat -A %s" % disk)
            output = commands.getoutput(cmd)
            if not self._validate_output(request, output):
                continue
            for attr, value in self._parse_output(request, output):
                stats.setdefault(attr, {})[disk] = value
        return stats

    def _get_adaptec_status(self, request, diskdict):
        stats = {}
        cmd = nagios.rootify("/usr/StorMan/arcconf getsmartstats 1")
        output = commands.getoutput(cmd)
        xml = output[output.index("<SmartStats"):output.index("</SmartStats>")+13]
        dom = parseString(xml)
        for disknode in dom.getElementsByTagName("PhysicalDriveSmartStats"):
            disk = diskdict[disknode.getAttribute("id")]
            for attrnode in disknode.getElementsByTagName("Attribute"):
                attrid = str(int(attrnode.getAttribute("id"), 16))
                stats.setdefault(attrid + ".VALUE", {})[disk] = attrnode.getAttribute("normalizedCurrent")
                stats.setdefault(attrid + ".THRESH", {})[disk] = attrnode.getAttribute("normalizedWorst")
                stats.setdefault(attrid + ".RAW_VALUE", {})[disk] = attrnode.getAttribute("rawValue")
        return stats

    def get_status_value(self, attr, request):
        if not hasattr(self, "stats") or self.stats is None:
            self.stats = self.retrieve_last_status(request)
        if ("fetchtime" not in self.stats
           or int(time.time()) - self.stats["fetchtime"] > request.interval):
                self.stats = self.retrieve_batch_status(request)
                self.stats["fetchtime"] = int(time.time())
                self.save_status(request, self.stats)
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
            cmd = nagios.rootify("/usr/sbin/smartctl -H %s" % disk)
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
        thresholds = self.get_status_value("1.THRESH", request)
        return self.get_result(request, sub_perfs, thresholds, 'raw read error rate')

    @plugin.command("SPIN_UP_TIME")
    def getSpinUpTime(self, request):
        sub_perfs = self.get_status_value("3.VALUE", request)
        thresholds = self.get_status_value("3.THRESH", request)
        return self.get_result(request, sub_perfs, thresholds, 'spin up time')

    @plugin.command("REALLOCATE_SECTOR_COUNT")
    def getReallocatedSectorCt(self, request):
        sub_perfs = self.get_status_value("5.VALUE", request)
        thresholds = self.get_status_value("5.THRESH", request)
        return self.get_result(request, sub_perfs, thresholds, 'sector reallocation')

    @plugin.command("SPIN_RETRY_COUNT")
    def getSpinRetryCount(self, request):
        sub_perfs = self.get_status_value("10.VALUE", request)
        thresholds = self.get_status_value("10.THRESH", request)
        return self.get_result(request, sub_perfs, thresholds, 'spin retries')

    @plugin.command("REALLOCATED_EVENT_COUNT")
    def getReallocatedEventCount(self, request):
        sub_perfs = self.get_status_value("196.VALUE", request)
        thresholds = self.get_status_value("196.THRESH", request)
        return self.get_result(request, sub_perfs, thresholds, 'reallocated events')

    @plugin.command("CUR_PENDING_SECTOR")
    def getCurrentPendingSector(self, request):
        sub_perfs = self.get_status_value("197.VALUE", request)
        thresholds = self.get_status_value("197.THRESH", request)
        return self.get_result(request, sub_perfs, thresholds, 'current pending sectors')

    @plugin.command("OFFLINE_UNCORRECTABLE")
    def getOfflineUncorrectable(self, request):
        sub_perfs = self.get_status_value("198.VALUE", request)
        thresholds = self.get_status_value("198.THRESH", request)
        return self.get_result(request, sub_perfs, thresholds, 'offline correctability')

    def get_result(self, request, sub_perfs, thresholds, message):
        status_code = nagios.Status.OK
        r = nagios.Result(request.type, status_code, message, request.appname)
        critical = request.crit
        for disk in sub_perfs:
            if not critical:
                critical = thresholds[disk]
            status_code = self.superimpose(status_code, sub_perfs[disk], request.warn, critical, reverse=True, exclusive=True)
            r.add_performance_data(disk, sub_perfs[disk], warn=request.warn, crit=critical)
        r.set_status_code(status_code)
        return r
        

if __name__ == "__main__":
    import sys
    SMARTChecker().run(sys.argv[1:])

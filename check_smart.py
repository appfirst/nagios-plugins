#!/usr/bin/env python
'''
Created on Aug 27, 2012

@author: Yangming
'''
import ucommands as commands
import nagios
import re
import time
from xml.dom.minidom import parseString
from nagios import CommandBasedPlugin as plugin
import sys

class SmartAttribute(object):
    def __init__(self):
        self.value = None
        self.threshold = None
        self.worst = None
        self.raw_value = None

class SmartChecker(nagios.BatchStatusPlugin):
    def __init__(self, *args, **kwargs):
        super(SmartChecker, self).__init__(*args, **kwargs)
        if sys.platform == "win32":
            self.parser.set_defaults(rootdir="c:\\temp\\")
        self.parser.add_argument("-f", "--filename", required=False, type=str, default='pd@smartctl')
        self.parser.add_argument("-z", "--appname",  required=False, type=str, default='smart')
        self.parser.add_argument("-D", "--disk",     required=False, type=str)
        self.parser.add_argument("-r", "--raid",     required=False, type=str, choices=["adaptec"])
        self.parser.add_argument("-p", "--path",     required=False, type=str, default="")
        #the interval (by sec) indicates how often this program will fetch smart info
        #if queried more frequently, it returns merely the last fetched info
        self.parser.add_argument("-i", "--interval", required=False, type=int, default=300)

    def _get_disks(self, request):
        if request.disk:
            disklist = [request.disk]
        else:
            output = commands.getoutput(self._get_smartctl(request) + " --scan")
            if self._validate_scan_output(request, output):
                disklist = []
                for line in output.split("\n"):
                    if line:
                        d = line.split("#")[0].strip()
                        disklist.append(d)
            elif sys.platform != "win32":
                cmd = nagios.rootify("/sbin/fdisk -l")
                output = commands.getoutput(cmd)
                disklist = re.findall(r"(?<=Disk )((?:/[\w-]+)+)(?=:)", output)
            else:
                nagios.StatusUnknownError(request, "Can't get disk list")
        return disklist

    def _get_smartctl(self, request):
        if sys.platform == "win32":
            return request.path + "smartctl"
        else:
            return nagios.rootify(request.path + "smartctl")

    def _validate_scan_output(self, request, output):
        if ("is not recognized as an internal or external command" in output
            or "No such file or directory" in output
            or "command not found" in output):
            raise nagios.StatusUnknownError(request, output)
        if ("=======> UNRECOGNIZED OPTION: scan" in output):
            return False
        else:
            return True

    def _validate_arcconf_output(self, request, output):
        if ( not output
            or "No such file or directory" in output
            or "command not found" in output):
            raise nagios.StatusUnknownError(request, "StorMan tool: arcconf is not available")
        else:
            return True

    def _validate_output(self, request, output):
        if ("=== START OF READ SMART DATA SECTION ===" in output
            or "SMART Health Status" in output):
            return True
        elif "Smartctl open device:" in output and "failed: No such device" in output:
            return False
        elif "SMART support is: Unavailable" in output:
            return True
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
                    attribute = SmartAttribute()
                    for metric, value in zip(metricset[2:], fields[2:]):
                        if metric == "VALUE":
                            attribute.value = value
                        elif metric == "THRESH":
                            attribute.threshold = value
                        elif metric == "WORST":
                            attribute.worst = value
                        elif metric == "RAW_VALUE":
                            attribute.raw_value = value
                    yield fields[0], attribute

    def _detect_adaptec(self, disklist, request):
        # map disk name to disk mount path
        adaptec_disks = {}
        diskset = set(disklist)
        for disk in diskset:
            cmd = nagios.rootify(self._get_smartctl(request) + " -a %s" % disk)
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

    def retrieve_adaptec_status(self, request, disklist):
        stats = {}
        diskdict = self._detect_adaptec(disklist, request)
        if not diskdict:
            return stats
        cmd = nagios.rootify("/usr/StorMan/arcconf getsmartstats 1")
        output = commands.getoutput(cmd)
        xml = output[output.index("<SmartStats"):output.index("</SmartStats>")+13]
        dom = parseString(xml)
        for disknode in dom.getElementsByTagName("PhysicalDriveSmartStats"):
            disk = diskdict[disknode.getAttribute("id")]
            for attrnode in disknode.getElementsByTagName("Attribute"):
                attribute = SmartAttribute()
                attribute.value = attrnode.getAttribute("normalizedCurrent")
                attribute.worst = attrnode.getAttribute("normalizedWorst")
                attribute.raw_value = attrnode.getAttribute("rawValue")
                attrid = str(int(attrnode.getAttribute("id"), 16))
                stats.setdefault(attrid, {})[disk] = attribute
        return stats

    def retrieve_batch_status(self, request):
        devicelist = self._get_disks(request)
        disklist = [d.split()[0] for d in devicelist if d]
        stats = {}

        # load the SMART info of adaptec raid controller
        if request.raid == "adaptec":
            stats.update(self.retrieve_adaptec_status(request, disklist))

        # load the SMART info of the rest disks.
        for device_with_type in devicelist:
            if device_with_type:
                disk = device_with_type.split()[0]
            else:
                continue
            cmd = nagios.rootify(self._get_smartctl(request) + (" -A %s" % device_with_type))
            output = commands.getoutput(cmd)
            if not self._validate_output(request, output):
                continue
            for attrid, attribute in self._parse_output(request, output):
                stats.setdefault(attrid, {})[disk] = attribute
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
    def get_overall_health(self, request):
        disklist = self._get_disks(request)

        # load the SMART info of adaptec raid controller
        status_code, message = self.check_health_status(request, disklist)
        r = nagios.Result(request.option, status_code, message, request.appname)
        return r

    def check_health_status(self, request, disklist):
        message = "overall test results"
        status_code = nagios.Status.OK
        for device_with_type in disklist:
            if device_with_type:
                disk = device_with_type.split()[0]
            else:
                continue
            cmd = nagios.rootify(self._get_smartctl(request) + " -H %s" % device_with_type)
            output = commands.getoutput(cmd)
            if not self._validate_output(request, output):
                continue
            if "SMART support is: Unavailable" in output:
                message += " %s=NOTSUPPORT" % disk
                continue
            test_result = re.findall(r"(?<=SMART overall-health self-assessment test result: )(\w+)", output)
            if not test_result:
                test_result = re.findall(r"(?<=SMART Health Status: )(\w+)", output)
            if not test_result:
                continue
            message += " %s=%s" % (disk, test_result[0])
            if test_result[0] != "PASSED" and test_result[0] != "OK":
                status_code = nagios.Status.CRITICAL
        return status_code, message

    def check_all_attribute(self, request, disklist):
        if not hasattr(self, "stats") or self.stats is None:
            stats = self.retrieve_last_status(request)
        if ("fetchtime" not in stats
           or int(time.time()) - stats["fetchtime"] > request.interval):
                stats = self.retrieve_batch_status(request)
                stats["fetchtime"] = int(time.time())
                self.save_status(request, stats)
        diskstats = {}
        status_code = nagios.Status.OK
        critical = request.crit
        message = "overall health "
        for diskattr in stats.itervalues():
            for device_with_type, attribute in diskattr.iteritems():
                disk = device_with_type.split()[0]
                disk_status_code = diskstats.setdefault(disk, nagios.Status.OK)
                if not critical:
                    critical = attribute.threshold
                disk_status_code = self.superimpose(disk_status_code, attribute.value, request.warn, critical,
                                 reverse=True, exclusive=True)
                if status_code < disk_status_code:
                    status_code = disk_status_code
                diskstats[disk] = disk_status_code
        if status_code > nagios.Status.OK:
            message += nagios.Status.to_status(status_code)
        for disk, stat in diskstats.iteritems():
            if stat > nagios.Status.OK:
                message += " disk %s status %s" % (disk, stat)
        return status_code, message

    @plugin.command("ADAPTEC_HEALTH")
    def get_adaptec_health(self, request):
        if sys.platform == "win32":
            raise nagios.StatusUnknownError(request, "Only Adaptec on linux are supported at the moment.")
        disklist = self._get_disks(request)
        diskdict = self._detect_adaptec(disklist, request)
        if not diskdict:
            raise nagios.StatusUnknownError(request, "No Adaptec Adaptec detected.")
        message = ""
        cmd = nagios.rootify("/usr/StorMan/arcconf getlogs 1 stats")
        output = commands.getoutput(cmd)
        if not self._validate_arcconf_output(request, output):
            return
        xml = output[output.index("<ControllerLog"):output.index("</ControllerLog>")+16]
        dom = parseString(xml)
        status_code = nagios.Status.OK
        if not request.warn:
            warn = 1
        else:
            warn = request.warn

        sub_perfs = []
        for statsnodee in dom.getElementsByTagName("physicaldrivestats"):
            value = int(statsnodee.getAttribute("smartWarnCnt"))
            disk = diskdict[statsnodee.getAttribute("id")]
            if value > 0:
                if message == "":
                    message = "smart warnings:"
                message += " %s=%s" % (disk, value)
            status_code = self.superimpose(status_code, value, warn, request.crit)
            sub_perfs.append((disk, value))

        if message == "":
            message = "no smart warning"
        r = nagios.Result(request.option, status_code, message, request.appname)
        for disk, value in sub_perfs:
            r.add_performance_data(disk, value, warn=warn, crit=request.crit)
        return r

    @plugin.command("RAW_READ_ERROR_RATE")
    def get_raw_read_error_rate(self, request):
        sub_perfs = self.get_status_value("1", request)
        return self.get_result(request, sub_perfs, 'raw read error rate')

    @plugin.command("SPIN_UP_TIME")
    def get_spin_up_time(self, request):
        sub_perfs = self.get_status_value("3", request)
        return self.get_result(request, sub_perfs, 'spin up time')

    @plugin.command("REALLOCATE_SECTOR_COUNT")
    def get_reallocated_sector_ct(self, request):
        sub_perfs = self.get_status_value("5", request)
        return self.get_result(request, sub_perfs, 'sector reallocation')

    @plugin.command("SPIN_RETRY_COUNT")
    def get_spin_retry_count(self, request):
        sub_perfs = self.get_status_value("10", request)
        return self.get_result(request, sub_perfs, 'spin retries')

    @plugin.command("REALLOCATED_EVENT_COUNT")
    def get_reallocated_event_count(self, request):
        sub_perfs = self.get_status_value("196", request)
        return self.get_result(request, sub_perfs, 'reallocated events')

    @plugin.command("CUR_PENDING_SECTOR")
    def get_current_pending_sector(self, request):
        sub_perfs = self.get_status_value("197", request)
        return self.get_result(request, sub_perfs, 'current pending sectors')

    @plugin.command("OFFLINE_UNCORRECTABLE")
    def get_offline_uncorrectable(self, request):
        sub_perfs = self.get_status_value("198", request)
        return self.get_result(request, sub_perfs, 'offline correctability')

    def get_result(self, request, sub_perfs, message):
        status_code = nagios.Status.OK
        r = nagios.Result(request.option, status_code, message, request.appname)
        critical = request.crit
        for disk, attribute in sub_perfs.iteritems():
            if not critical:
                critical = attribute.threshold
            status_code = self.superimpose(status_code, attribute.value, request.warn, critical, reverse=True)
            r.add_performance_data(disk, attribute.value, warn=request.warn, crit=critical)
        r.set_status_code(status_code)
        return r

if __name__ == "__main__":
    SmartChecker().run(sys.argv[1:])

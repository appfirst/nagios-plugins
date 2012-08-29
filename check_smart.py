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

    def _get_batch_status(self, request):
        if request.disk:
            output = commands.getoutput("sudo /sbin/fdisk -l")
            disks = re.findall(r"(?<=Disk )((?:/[\w-]+)+)(?=:)", output)
        return commands.getoutput("sudo smartctl -d sat -A %s" % disks[0])

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
            if "Pre-fail" in l or "ID#" in l:
                fields = l.split()
                if fields[0] == "ID#":
                    metricset = fields
                if fields[0].isdigit() and len(fields) == len(metricset):
                    for metric, value in zip(metricset[2:], fields[2:]):
                        k = "%s.%s" % (fields[1], metric)
                        yield k, value

    def get_status_value(self, attr, request):
        sub_perfs = []
        for disk in self._get_disks(request):
            output = commands.getoutput("sudo smartctl -d sat -A %s" % disk)
            if not self._validate_output(request, output):
                break
            for k, value in self._parse_output(request, output):
                if k == attr:
                    sub_perfs.append((disk, value));
        return sub_perfs;

    @plugin.command("RAW_READ_ERROR_RATE")
    def getRawReadErrorRate(self, request):
        sub_perfs = self.get_status_value("Raw_Read_Error_Rate.RAW_VALUE", request)
        status_code = nagios.Status.OK
        r = nagios.Result(request.type, status_code, 'raw read error rate is %s' % nagios.Status.to_status(status_code), request.appname);
        for disk, pfvalue in sub_perfs:
            status_code = self.superimpose(status_code, pfvalue, request)
            r.add_performance_data(disk, pfvalue, warn=request.warn, crit=request.crit)
        r.set_status_code(status_code)
        return r

    @plugin.command("SPIN_UP_TIME")
    def getSpinUpTime(self, request):
        sub_perfs = self.get_status_value("Spin_Up_Time.RAW_VALUE", request)
        status_code = nagios.Status.OK
        r = nagios.Result(request.type, status_code, 'spin up time is %s' % nagios.Status.to_status(status_code), request.appname);
        for disk, pfvalue in sub_perfs:
            status_code = self.superimpose(status_code, pfvalue, request)
            r.add_performance_data(disk, pfvalue, warn=request.warn, crit=request.crit)
        r.set_status_code(status_code)
        return r

    @plugin.command("REALLOCATE_SECTOR_COUNT")
    def getReallocatedSectorCt(self, request):
        sub_perfs = self.get_status_value("Reallocated_Sector_Ct.RAW_VALUE", request)
        status_code = nagios.Status.OK
        r = nagios.Result(request.type, status_code, 'sector reallocated is %s' % nagios.Status.to_status(status_code), request.appname);
        for disk, pfvalue in sub_perfs:
            status_code = self.superimpose(status_code, pfvalue, request)
            r.add_performance_data(disk, pfvalue, warn=request.warn, crit=request.crit)
        r.set_status_code(status_code)
        return r

if __name__ == "__main__":
    import sys
    SMARTChecker().run(sys.argv[1:])

'''
Created on Jul 9, 2012

@author: Yangming


all the exceptions need to inherit from StatusUnknown
in order to be captured in nagios.BasePlugin.run()
'''
from nagios import Result, Status
from exceptions import Exception

class StatusUnknown(Exception):
    def __init__(self, request, msg="failed to check status. check arguments and try again."):
        self.status_type = request.type
        self.status = Status.UNKNOWN
        self.msg = msg

    def __str__(self):
        return self.msg

    @property
    def result(self):
        return Result(self.status_type, self.status, self.msg)

class ServiceInaccessible(StatusUnknown):
    def __init__(self, request, msg="service is not accessible."):
        self.status_type = request.type
        self.status = Status.CRITICAL
        self.msg = msg

class AuthenticationFailed(StatusUnknown):
    def __init__(self, request, msg="authentication failed."):
        self.status_type = request.type
        self.status = Status.UNKNOWN
        self.msg = msg

class OutputFormatError(StatusUnknown):
    def __init__(self, request, msg="output format is not as expected."):
        self.status_type = request.type
        self.status = Status.UNKNOWN
        self.msg = msg

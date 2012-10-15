'''
Created on Oct 7, 2012

a thin wrap of subprocess module as an adapter to commands module

@author: Yangming
'''
import subprocess

def getstatusoutput(cmd):
    '''
    Execute the string cmd in a shell with subprocess.check_call() and return a 2-tuple (status, output).
    cmd is actually run as { cmd ; } 2>&1, so that the returned output will contain output or error messages.
    A trailing newline is stripped from the output.
    The exit status for the command can be interpreted according to the rules for the C function wait().
    '''
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
        return 0, output
    except subprocess.CalledProcessError, e:
        return e.returncode, e.output

def getoutput(cmd):
    '''
    Like getstatusoutput(), except the exit status is ignored and the return value is a string containing the command output.
    '''
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
        return output
    except subprocess.CalledProcessError, e:
        return e.output

def getstatus(filename):
    '''
    Return the output of ls -ld file as a string. 
    This function uses the getoutput() function, and properly escapes backslashes and dollar signs in the argument.
    Deprecated since version 2.6: This function is nonobvious and useless. The name is also misleading in the presence of getstatusoutput().
    '''
    f = open(filename, "r")
    return getoutput(f)
#!/usr/bin/env python

"""
Author: Tony Ling
Reads and parses Couchbase cbstats tool.  This script work as a wrapper around 'cbstats all'.
Metrics the user can choose from can be any of the keys turned from cbstats 'all' option.
All warnings are triggered if metric values are greater than thresholds
except for uptime and total requests which have no warning thresholds.
For a list of all metrics, run '/opt/couchbase/bin/cbstats [host]:[port] all' in terminal.

Example Usage:
  python check_couchbase.py -t curr_connections -W 100 -C 150

Created on: 12/05/14
"""
import sys
import argparse
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('-H', '--host', help='Host location, default=localhost', default='localhost')
parser.add_argument('-P', '--port', help='Port number, default=11210', default='11210')
parser.add_argument('-W', '--warning', help='Warning threshold', default=None, type=float)
parser.add_argument('-C', '--critical', help='Critical theshold', default=None, type=float)
parser.add_argument('-b', '--bucket', help='Bucket name, default=\'default\'', default='default')
parser.add_argument('-p', '--password', help='Bucket password if required', default=None)
parser.add_argument('-t', '--metric', help='Metric to choose from \'cbstats all\' output', default=None, required=True)
args = parser.parse_args()

def print_status(status, msg, value, metric):
	if status is 2:
		print "CRITICAL - " + msg + ": " + str(value) +  "|" +  metric  + "=" + str(value)
	elif status is 1:
		print "WARNING - " + msg + ": " + str(value) +  "|" + metric  + "=" + str(value)
	else:
		print "OK - " + msg + ": " + str(value) + "|" + metric  + "=" + str(value)

def process_output(output):
	status_code = 3
	g = subprocess.Popen(["grep", "{m}".format(m=args.metric)], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
	out = g.communicate(input=output)[0].strip().split('\n')
	found = False
	if len(out) > 1:
		for ele in out:
			if (ele.split(":")[0].strip() == args.metric):
				found = True
				value = ele.split(":")[1].strip()
	else:
		if out[0] is "":
			pass
		else:
			found = True
			value = out[0].split()[1]
	if not found:
		print "Error {m} metric not found in 'cbstats all'".format(m=args.metric)
	else:
		try:
			if (args.critical and int(value) >= args.critical):
				status_code = 2
				print_status(status_code, args.metric, value, args.metric)
			elif (args.warning and int(value) >= args.warning):
				status_code = 1
				print_status(status_code, args.metric, value, args.metric)
			else:
				status_code = 0
				print_status(status_code, args.metric, value, args.metric)
		except: # catches attempts at trying to compare a string with a threshold value
			status_code = 0
			print_status(status_code, args.metric, value, args.metric)
	return status_code

# code starts here
status_code = 3
if (args.critical and args.critical < 0):
	print "Error: -C Critical cannot be negative"
elif (args.warning and args.warning < 0):
	print "Error: -W Warning cannot be negative"
else:
	if (args.password):
		p = subprocess.Popen(["/opt/couchbase/bin/cbstats", "{host}:{port}".format(host=args.host, port=args.port), "-b", "{bucket}".format(bucket=args.bucket), "-p", "{passw}".format(passw=args.password), "all"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
		out, err = p.communicate()
		status_code = sysprocess_output(out)
	else:
		p = subprocess.Popen(["/opt/couchbase/bin/cbstats", "{host}:{port}".format(host=args.host, port=args.port), "-b", "{bucket}".format(bucket=args.bucket), "all"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
		out, err = p.communicate()
		status_code = process_output(out)
sys.exit(status_code)

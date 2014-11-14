#!/usr/bin/env python

"""
Author: Tony Ling
Checks apache2 server-status page and parses the output depending on the metric argument.
Access to /server-status webpage is required.
For use with AppFirst collector

Example Usage:
  python /usr/share/appfirst/plugins/libexec/check_apache.py -H localhost -P 80 -t busy_workers -W 110 -C 130

Created on: 8/22/14
"""

import sys
import argparse
import urllib2

status_code = 3;

# metrics dict keys are just script arguments
# key values are either metrics or scoreboard arrays
# scoreboard values arrays contain scoreboard key and output string
metrics = {}
metrics['total_accesses'] = 'Total Accesses'
metrics['cpu_load'] = 'CPULoad'
metrics['uptime'] = 'Uptime'
metrics['bytes_per_req'] = 'BytesPerReq'
metrics['bytes_per_sec'] = 'BytesPerSec'
metrics['req_per_sec'] = 'ReqPerSec'
metrics['total_kbytes'] = 'Total kBytes'
metrics['busy_workers'] = 'BusyWorkers'
metrics['idle_workers'] = 'IdleWorkers'
metrics['scoreboard_c'] = ['C', 'Closing connection']
metrics['scoreboard_.'] = ['.', 'Open slot with no current process']
metrics['scoreboard_d'] = ['D', 'DNS lookup']
metrics['scoreboard_g'] = ['G', 'Gracefully finishing']
metrics['scoreboard_i'] = ['I', 'Idle cleanup of worker']
metrics['scoreboard_k'] = ['K', 'Keepalive']
metrics['scoreboard_l'] = ['L', 'Logging']
metrics['scoreboard_r'] = ['R', 'Reading request']
metrics['scoreboard_w'] = ['W', 'Sending reply']
metrics['scoreboard__'] = ['_', 'Waiting for connection']
metrics['scoreboard_s'] = ['S', 'Starting up']

parser = argparse.ArgumentParser()
parser.add_argument('-H', '--host', help='Host location, default=localhost', default='localhost')
parser.add_argument('-P', '--port', help='Port number, default=80', default='80')
parser.add_argument('-W', '--warning', help='Warning threshold', default=None, type=float)
parser.add_argument('-C', '--critical', help='Critical theshold', default=None, type=float)
parser.add_argument('-t', '--metric', help='Metric to choose', default=None, required=True)

args = parser.parse_args()
try:
	cmd = metrics[args.metric]
	if (isinstance(cmd, list)):
		scoreboard = True
		msg = cmd[1]
		key = cmd[0]
		cmd = 'Scoreboard'
	else:
		scoreboard = False
		msg = args.metric
except KeyError:
	print "Error: Unrecognized/unsupported metric '{_metric}'".format(_metric=args.metric)
	str_metrics =  "Supported Metrics: ["
	for metric in metrics:
		str_metrics += ("'" + metric + "',")
	print str_metrics[:-1] + "]"
	sys.exit(status_code)

if (args.critical and args.critical < 0):
	print "Error: -C Critical cannot be negative"
	sys.exit(status_code)
elif (args.warning and args.warning < 0):
	print "Error: -W Warning cannot be negative"
	sys.exit(status_code)

#default url = "http://localhost:80/server-status?auto"
url = "http://{host}:{port}/server-status?auto".format(host=args.host,port=args.port)

apache_stats = urllib2.urlopen(url).read().split('\n')
if (scoreboard):
	keycounter = 0
	for line in apache_stats:
		tokens = line.split(': ')
		if (tokens[0] == cmd):
			for worker in tokens[1]:
				if (worker == key):
					keycounter += 1
			strkeycounter = str(keycounter)
			if (args.critical and keycounter >= args.critical):
				print "CRITICAL - " + msg + ": " + strkeycounter + "|" + msg + "=" + strkeycounter
				status_code = 2
			elif (args.warning and keycounter >= args.warning):
				print "WARNING - " + msg + ": " + strkeycounter + "|" + msg + "=" + strkeycounter
				status_code = 1
			else:
				print "OK - " + msg + ": " + strkeycounter + "|" + msg + "=" + strkeycounter
				status_code = 0
else:
	for line in apache_stats:
		tokens = line.split(': ')
		if (tokens[0] == cmd):
			if (args.critical and float(tokens[1]) >= args.critical):
				print "CRITICAL - " + tokens[0] + ": " + tokens[1] + "|" + msg + "=" + tokens[1]
				status_code = 2
			elif (args.warning and float(tokens[1]) >= args.warning):
				print "WARNING - " + tokens[0] + ": " + tokens[1] + "|" + msg + "=" + tokens[1]
				status_code = 1
			else:
				print "OK - " + tokens[0] + ": " + tokens[1] + "|" + msg + "=" + tokens[1]
				status_code = 0
sys.exit(status_code)

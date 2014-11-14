#!/usr/bin/env python

"""
Author: Tony Ling
Executes a zookeeper 4 letter command and parses the output depending on the metric argument.
The script uses netcat 'nc' command. For use with AppFirst collector.

Example Usage:
  python check_zookeeper.py -t connections -H localhost -P 2181 -W 100 -C 200

Created on: 8/26/14
"""

import sys
import subprocess
import argparse

status_code = 3;

# metrics dict keys are script metric -t arguments, key values are array values
# Elements: 1=nc command to zk server, 2=metric to obtain, 3=script output string
metrics = {}
metrics['mode'] = ['stat', 'Mode', 'Server Mode']
metrics['connections'] = ['stat', 'Connections', 'Number of client connections']
metrics['connections_outstanding'] = ['stat', 'Outstanding', 'Number of outstanding requests']
metrics['zk_znode_count']= ['mntr', 'zk_znode_count', 'Zookeeper Znode count']
metrics['zk_min_latency']= ['mntr', 'zk_min_latency', 'Zookeeper min latency']
metrics['zk_max_latency']= ['mntr', 'zk_max_latency', 'Zookeeper max latency']
metrics['zk_avg_latency']= ['mntr', 'zk_avg_latency', 'Zookeeper avg latency']

parser = argparse.ArgumentParser()
parser.add_argument('-H', '--host', help='Host location, default=localhost', default='localhost')
parser.add_argument('-P', '--port', help='Port number, default=2181', default='2181')
parser.add_argument('-W', '--warning', help='Warning threshold', default=None, type=float)
parser.add_argument('-C', '--critical', help='Critical theshold', default=None, type=float)
parser.add_argument('-t', '--metric', help='Metric to choose', default=None, required=True)

args = parser.parse_args()

if (args.critical and args.critical < 0):
	print "Error: -C Critical cannot be negative"
	sys.exit(status_code)
elif (args.warning and args.warning < 0):
	print "Error: -W Warning cannot be negative"
	sys.exit(status_code)
try:
	array_value = metrics[args.metric]
	cmd = array_value[0]
	metric = array_value[1]
	msg = array_value[2]
	zk_info = subprocess.Popen(['nc', args.host, args.port], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
	output, err = zk_info.communicate(input=cmd)
except KeyError:
	print "Error: Unrecognized/unsupported metric '{_metric}'".format(_metric=args.metric)
	str_metrics =  "Supported Metrics: ["
	for metric in metrics:
		str_metrics += ("'" + metric + "',")
	print str_metrics[:-1] + "]"
	sys.exit(status_code)

for line in output.split('\n'):
	if (cmd == 'stat'):
		tokens = line.split(':')
	elif (cmd == 'mntr'):
		tokens = line.split('\t')
	else:
		break
	if (tokens[0] == metric):
		try:
			if (args.critical and float(tokens[1]) >= args.critical):
				print "CRITICAL - " + msg + ": " + tokens[1] +  "|" +  metric + "=" + tokens[1]
				status_code = 2
			elif (args.warning and float(tokens[1]) >= args.warning):
				print "WARNING - " + msg + ": " + tokens[1] +  "|" + metric + "=" + tokens[1]
				status_code = 1
			else:
				print "OK - " + msg + ": " + tokens[1] + "|" + metric + "=" + tokens[1]
				status_code = 0
		except ValueError:
			print "OK - " + msg + ": " + tokens[1] + "|" + metric + "=" + tokens[1]
			status_code = 0
		break

sys.exit(status_code)

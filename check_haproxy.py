#!/usr/bin/env python

"""
Author: Tony Ling
Checks haproxy stats page and parses the output depending on the metric.
The script adds up the total metric values of all servers.
For use with AppFirst collector

Example Usage:
  python /usr/share/appfirst/plugins/libexec/check_haproxy.py -P 1935 -L haproxy?stats -U guest -p guest -t qcur -W 500 -C 1000

Created on: 8/22/14
"""

import sys
import argparse
import urllib2
import csv
import base64
import StringIO

status_code = 3;

#metrics dict key is the cvs column metric and value is output string
metrics = {}
metrics['econ'] = 'Total connection errors'
metrics['ereq'] = 'Total error requests'
metrics['eresp'] = 'Total error responses'
metrics['qcur'] = 'Total current queues'
metrics['scur'] = 'Total current sessions'
metrics['stot'] = 'Total sessions'

parser = argparse.ArgumentParser()
parser.add_argument('-H', '--host', help='Host location, default=localhost', default='localhost')
parser.add_argument('-P', '--port', help='Port number', default=None, type=int)
parser.add_argument('-U', '--username', help='Username for authentication, default=guest', default='guest')
parser.add_argument('-p', '--password', help='Password for authentication, default=guest', default='guest')
parser.add_argument('-L', '--location', help='Path location of stats page, ex: [host]:[port]/haproxy?stats', default=None)
parser.add_argument('-W', '--warning', help='Warning threshold', default=None, type=float)
parser.add_argument('-C', '--critical', help='Critical theshold', default=None, type=float)
parser.add_argument('-t', '--metric', help='Metric to choose', default=None, required=True)

args = parser.parse_args()
try:
	msg = metrics[args.metric]
	metric = args.metric
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

#example url = "http://localhost:1935/haproxy?stats;csv"
if (args.port):
	if (args.location):
		request = urllib2.Request("http://{host}:{port}/{path};csv".format(host=args.host,port=args.port,path=args.location))
	else:
		print "Error: No path location supplied.  Type -h or --help for help"
		sys.exit(2)
else:
	print "Error: No port supplied.  Type -h or --help for help"
	sys.exit(2)

if (args.username and args.password):
	base64string = base64.encodestring('%s:%s' % (args.username, args.password)).replace('\n', '')
	request.add_header("Authorization", "Basic %s" % base64string)

csvstring = StringIO.StringIO(urllib2.urlopen(request).read())
reader = csv.reader(csvstring, delimiter=',')

data = []
for row in reader:
	data.append(row)
limit = len(data[0])

for i in range(0,limit):
	if (data[0][i] == metric):
		index = i;
		break;
metric_value = 0
for i in range(1,len(data)):
	if (data[i][index] is not ''):
		try:
			metric_value += int(data[i][index])
		except:
			pass

if (args.critical and metric_value >= args.critical):
	print "CRITICAL - " + msg + ": " + str(metric_value) + "|" + metric + "=" + str(metric_value)
	status_code = 2
elif (args.warning and metric_value >= args.warning):
	print "WARNING - " + msg + ": " + str(metric_value) + "|" + metric + "=" + str(metric_value)
	status_code = 1
else:
	print "OK - " + msg + ": " + str(metric_value) + "|" + metric + "=" + str(metric_value)
	status_code = 0

sys.exit(status_code)

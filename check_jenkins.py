#!/usr/bin/env python

"""
Author: Tony Ling
Uses Jenkins HTTP API for server metrics and parses the output
Metrics supported: mode, quietingDown, useCrumbs, views, buildQueue, executorsUtilization
Warnings if metric value is less than threshold: views
Warnings if metric value is greater than threshold: executorsUtilization, buildQueue

Example Usage:
  python check_jenkins.py -t executorsUtilization -H localhost -P 8080 -W 80 -C 90

Created on: 10/31/14
"""

import sys
import urllib2
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-H', '--host', help='Host location, default=localhost', default='localhost')
parser.add_argument('-P', '--port', help='Port number, default=8080', default='8080')
parser.add_argument('-W', '--warning', help='Warning threshold', default=None, type=float)
parser.add_argument('-C', '--critical', help='Critical theshold', default=None, type=float)
parser.add_argument('-t', '--metric', help='Metric to choose', default=None, required=True)
args = parser.parse_args()

def check_thresholds():
	if (args.critical and args.critical < 0):
		print "Error: -C Critical cannot be negative"
		sys.exit(status_code)
	elif (args.warning and args.warning < 0):
		print "Error: -W Warning cannot be negative"
		sys.exit(status_code)

def cmp_less(msg, value):
	check_thresholds()
	if (args.critical and float(value) <= args.critical):
		print "CRITICAL - " + msg + ": " + str(value) +  "|" +  args.metric  + "=" + str(value)
		status_code = 2
	elif (args.warning and float(value) <= args.warning):
		print "WARNING - " + msg + ": " + str(value) +  "|" + args.metric  + "=" + str(value)
		status_code = 1
	else:
		print "OK - " + msg + ": " + str(value) + "|" + args.metric  + "=" + str(value)
		status_code = 0
	sys.exit(status_code)

def cmp_greater(msg, value):
	check_thresholds()
	if (args.critical and float(value) >= args.critical):
		print "CRITICAL - " + msg + ": " + str(value) +  "|" +  args.metric  + "=" + str(value)
		status_code = 2
	elif (args.warning and float(value) >= args.warning):
		print "WARNING - " + msg + ": " + str(value) +  "|" + args.metric  + "=" + str(value)
		status_code = 1
	else:
		print "OK - " + msg + ": " + str(value) + "|" + args.metric  + "=" + str(value)
		status_code = 0
	sys.exit(status_code)

def get_mode():
	metrics = get_jenkins_metrics("api/json")
	status = metrics[args.metric]
	if status == "NORMAL":
		print "OK - Server mode: " + status + "|" + args.metric + "=" + status
		status_code = 0
		sys.exit(status_code)
	else:
		print "WARNING - Server mode: " + status + "|" + args.metric + "=" + status
		status_code = 1
		sys.exit(status_code)

def get_quietingDown():
	metrics = get_jenkins_metrics("api/json")
	status = str(metrics[args.metric])
	print "OK - Server is quieting down: " + status + "|" + args.metric + "=" + status
	status_code = 0
	sys.exit(status_code)

def get_useCrumbs():
	metrics = get_jenkins_metrics("api/json")
	status = str(metrics[args.metric])
	print "OK - Server is using crumbs: " + status + "|" + args.metric + "=" + status
	status_code = 0
	sys.exit(status_code)

def get_views():
	metrics = get_jenkins_metrics("api/json")
	value = len(metrics[args.metric])
	msg = "Number of views"
	cmp_less(msg, value)

def get_buildQueue():
	metrics = get_jenkins_metrics("queue/api/json")
	value = len(metrics["items"])
	msg = "Number of build queue items"
	cmp_greater(msg, value)

def get_executorsUtilization():
	metrics = get_jenkins_metrics("computer/api/json")
	busy = int(metrics["busyExecutors"])
	total = float(metrics["totalExecutors"])
	percent = busy/total
	msg = "Executors Utilization (%)"
	cmp_greater(msg, percent)

def get_jenkins_metrics(url):
	try:
		output = urllib2.urlopen("http://{host}:{port}/{url}".format(host=args.host, port=args.port, url=url))
		jenkins_metrics = json.loads(output.read())
	except KeyError:
		print "Error: Unrecognized/unsupported metric '{_metric}'".format(_metric=args.metric)
		str_metrics =  "Supported Metrics: ["
		for metric in metrics:
			str_metrics += ("'" + metric + "',")
		print str_metrics[:-1] + "]"
		sys.exit(status_code)
	except urllib2.URLError:
		print "Error: Connection Refused - Check host and port arguments"
		sys.exit(status_code)
	return jenkins_metrics

# metrics dict keys are script metric -t arguments
# key values are functions called when the keys are matched
metrics = { "mode": get_mode,
            "quietingDown": get_quietingDown,
            "useCrumbs": get_useCrumbs,
            "views": get_views,
            "buildQueue": get_buildQueue,
            "executorsUtilization": get_executorsUtilization
            }

# Program entry starts here
status_code = 3
try:
	metrics[args.metric]()
except KeyError:
	print "Error: Unrecognized/unsupported metric '{_metric}'".format(_metric=args.metric)
	str_metrics =  "Supported Metrics: ["
	for metric in metrics:
		str_metrics += ("'" + metric + "',")
	print str_metrics[:-1] + "]"
	sys.exit(status_code)


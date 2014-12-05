#!/usr/bin/env python

"""
Author: Tony Ling
Reads and parses OpenLiteSpeed live statistics file /tmp/lshttpd/.rtreport.
All warnings are triggered if metric values are greater than thresholds
except for uptime and total requests which have no warning thresholds.

Example Usage:
  python check_openlitespeed.py -t connections_utilized -W 80 -C 90

Created on: 11/21/14
"""

import sys
import argparse

def get_status_code(value, compare):
	status_code = 3
	if compare is None:
		status_code = 0
	elif compare == "greater":
		if (args.critical and int(value) >= args.critical):
			status_code = 2
		elif (args.warning and int(value) >= args.warning):
			status_code = 1
		else:
			status_code = 0
	else:
		if (args.critical and int(value) <= args.critical):
			status_code = 2
		elif (args.warning and int(value) <= args.warning):
			status_code = 1
		else:
			status_code = 0
	return status_code

def print_status(status, msg, value, metric):
	if status is 2:
		print "CRITICAL - " + msg + ": " + str(value) +  "|" +  metric  + "=" + str(value)
	elif status is 1:
		print "WARNING - " + msg + ": " + str(value) +  "|" + metric  + "=" + str(value)
	else:
		print "OK - " + msg + ": " + str(value) + "|" + metric  + "=" + str(value)

def handle_metric_utilization(conn, max_conn, msg, compare, metric):
	value = float(conn)/float(max_conn)
	print_status(get_status_code(value, compare), msg, value, metric)

def handle_metric(metric, value, msg, compare):
	if metric == "UPTIME:":
		time = value.split(":")
		print_status(0, msg, (int(time[0])*3600)+(int(time[1])*60)+int(time[2]), metric)
	else:
		print_status(get_status_code(value, compare), msg, value, metric)

# metrics dict keys are script metric -t arguments
# key list values: element 0 = script output string, 1= metrics to parse for,
#  2 = greater than/less than/status for critical/warning values
metrics = {}
metrics['uptime'] = ['Server uptime in seconds', 'UPTIME:', None]
metrics['bytes_in'] = ['HTTP Bytes per second in', 'BPS_IN:', 'greater']
metrics['bytes_out'] = ['HTTP Bytes per second out', 'BPS_OUT:', 'greater']
metrics['https_bytes_in']= ['HTTPS Bytes per second in', 'SSL_BPS_IN:', 'greater']
metrics['https_bytes_out']= ['HTTPS Bytes per second out', 'SSL_BPS_OUT:', 'greater']
metrics['connections']= ['HTTP connections', 'PLAINCONN:', 'greater']
metrics['connections_utilized']= ['HTTP connections utilized(current/max)', None, 'greater']
metrics['idle_connections']= ['Idle HTTP connections', 'IDLECONN:', 'greater']
metrics['https_connections']= ['HTTPS connections', 'SSLCONN:', 'greater']
metrics['https_connections_utilized']= ['HTTPS connections utilized(current/max)', None, 'greater']
metrics['requests_processing']= ['Total requests processing', 'REQ_PROCESSING:', 'greater']
metrics['requests_per_second']= ['Total requests per second', 'REQ_PER_SEC:', 'greater']
metrics['total_requests']= ['Total requests', 'TOT_REQS:', None]

parser = argparse.ArgumentParser()
parser.add_argument('-W', '--warning', help='Warning threshold', default=None, type=float)
parser.add_argument('-C', '--critical', help='Critical theshold', default=None, type=float)
parser.add_argument('-t', '--metric', help='Metric to choose', default=None, required=True)
args = parser.parse_args()

# code starts here
status_code = 3
if (args.critical and args.critical < 0):
	print "Error: -C Critical cannot be negative"
	sys.exit(status_code)
elif (args.warning and args.warning < 0):
	print "Error: -W Warning cannot be negative"
	sys.exit(status_code)
try:
	array_value = metrics[args.metric]
	with open("/tmp/lshttpd/.rtreport") as file:
		line = file.readline()
		if "Open" not in line:
			print("Error: OpenLiteSpeed version does not match, perhaps Standard or Enterprise LiteSpeed is installed instead")
			sys.exit(status_code)
		conn = ""
		max_conn = ""
		while line:
			line = file.readline()
			metrics = line.strip().split(",")
			if "[]" not in metrics[0]:
				for metric in metrics:
					metric = metric.strip().split(" ")
					if args.metric == "connections_utilized":
						breakout = True
						if metric[0] == "PLAINCONN:":
							conn = metric[1]
						elif metric[0] == "MAXCONN:":
							max_conn = metric[1]
						if conn != "" and max_conn != "":
							status_code = handle_metric_utilization(conn, max_conn, array_value[0], array_value[2], "CONN_UTILIZED")
							break
					elif args.metric == "https_connections_utilized":
						breakout = True
						if metric[0] == "SSLCONN:":
							conn = metric[1]
						elif metric[0] == "MAXSSL_CONN:":
							max_conn = metric[1]
						if conn != "" and max_conn != "":
							status_code = handle_metric_utilization(conn, max_conn, array_value[0], array_value[2], "SSLCONN_UTILIZED")
							break
					else:
						if metric[0] == array_value[1]:
							status_code = handle_metric(metric[0], metric[1], array_value[0], array_value[2])
							line = ""
							break
			else:
				for metric in metrics:
					metric = metric.strip().split(" ")
					if metric[-2] == array_value[1]:
						status_code = handle_metric(metric[-2], metric[-1], array_value[0], array_value[2])
						break 
				break
	sys.exit(status_code)
except KeyError:
	print "Error: Unrecognized/unsupported metric '{_metric}'".format(_metric=args.metric)
	str_metrics =  "Supported Metrics: ["
	for metric in metrics:
		str_metrics += ("'" + metric + "',")
	print str_metrics[:-1] + "]"
	sys.exit(status_code)

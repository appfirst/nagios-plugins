#!/usr/bin/env python

"""
Author: Tony Ling
Checks nginx server status page and parses the output depending on the metric argument.
Requires nginx to have --with-http_stub_status_module
For use with AppFirst collector

Example Usage:
  python /usr/share/appfirst/plugins/libexec/check_nginx.py -H localhost -P 80 -L status -t waiting -W 10 -C 20


Created on: 11/14/14
"""

import sys
import argparse
import urllib2
import re

status_code = 3

def cmp_greater(msg, metric, value):
	check_thresholds()
	if (args.critical and float(value) >= args.critical):
		print "CRITICAL - " + str(msg) + ": " + str(value) +  "|" +  str(metric)  + "=" + str(value)
		status_code = 2
	elif (args.warning and float(value) >= args.warning):
		print "WARNING - " + str(msg) + ": " + str(value) +  "|" + str(metric)  + "=" + str(value)
		status_code = 1
	else:
		print "OK - " + str(msg) + ": " + str(value) + "|" + str(metric)  + "=" + str(value)
		status_code = 0
	sys.exit(status_code)

#Due to how the output of the status page is formated, different functions are used for different metrics
def accepted_conn(nginx_stats):
	cmd = 'accepts'
	output = "Accepted connections: "
	server_metrics = False
	metric_index = 0
	for line in nginx_stats:
		tokens = line.split(' ')	
		if (server_metrics):
			cmp_greater(output, "accepted_connections", tokens[metric_index])
		else:
			for i in range(len(tokens)):
				if (tokens[i] == cmd):
					server_metrics = True
					metric_index = i

def active_conn(nginx_status):
	cmd = 'Active connections'
	for line in nginx_stats:
		tokens = line.split(': ')
		for i in range(len(tokens)):
			if (tokens[i] == cmd):
				cmp_greater(tokens[i], "active_connections", tokens[i+1])

def handled_conn(nginx_status):
	cmd = 'handled'
	output = "Handled connections: "
	server_metrics = False
	metric_index = 0
	for line in nginx_stats:
		tokens = line.split(' ')	
		if (server_metrics):
			cmp_greater(output, "handled_connections", tokens[metric_index])
		else:
			for i in range(len(tokens)):
				if (tokens[i] == cmd):
					server_metrics = True
					metric_index = i

def handled_req(nginx_status):
	cmd = 'requests'
	output = "Handled requests: "
	server_metrics = False
	metric_index = 0
	for line in nginx_stats:
		tokens = line.split(' ')	
		if (server_metrics):
			cmp_greater(output, "handled_requests", tokens[metric_index])
		else:
			for i in range(len(tokens)):
				if (tokens[i] == cmd):
					server_metrics = True
					metric_index = i

def req_per_conn(nginx_status):
	cmd = 'handled'
	output = "Request per connection: "
	server_metrics = False
	m_i = 0
	for line in nginx_stats:
		tokens = line.split(' ')	
		if (server_metrics):
			req_per_conn = float(int(tokens[m_i+1]))/float(int(tokens[m_i]))
			cmp_greater(output, "req_per_conn", req_per_conn)
		else:
			for i in range(len(tokens)):
				if (tokens[i] == cmd):
					server_metrics = True
					m_i = i

def reading(nginx_status):
	cmd = 'Reading:'
	for line in nginx_stats:
		tokens = line.split(' ')
		for i in range(len(tokens)):
			if (tokens[i] == cmd):
				cmp_greater(tokens[i], "reading", tokens[i+1])

def waiting(nginx_status):
	cmd = 'Waiting:'
	for line in nginx_stats:
		tokens = line.split(' ')
		for i in range(len(tokens)):
			if (tokens[i] == cmd):
				cmp_greater(tokens[i], "waiting", tokens[i+1])

def writing(nginx_status):
	cmd = 'Writing:'
	for line in nginx_stats:
		tokens = line.split(' ')
		for i in range(len(tokens)):
			if (tokens[i] == cmd):
				cmp_greater(tokens[i], "writing", tokens[i+1])

# Metrics dict storing functions as values
metrics = {'accepted_connections' : accepted_conn,
           'active_connections' : active_conn,
           'handled_connections' : handled_conn,
           'handled_requests' : handled_req,
           'requests_per_connection' : req_per_conn,
           'reading' : reading,
           'waiting' : waiting,
           'writing' : writing
           }

parser = argparse.ArgumentParser()
parser.add_argument('-H', '--host', help='Host location, default=localhost', default='localhost')
parser.add_argument('-P', '--port', help='Port number, default=80', default='80')
parser.add_argument('-L', '--location', help='location of status page, default=status', default='status')
parser.add_argument('-W', '--warning', help='Warning threshold', default=None, type=int)
parser.add_argument('-C', '--critical', help='Critical theshold', default=None, type=int)
parser.add_argument('-t', '--metric', help='Metric to choose', default=None, required=True)
args = parser.parse_args()

if (args.critical and args.critical < 0):
	print "Error: -C Critical cannot be negative"
	sys.exit(status_code)
elif (args.warning and args.warning < 0):
	print "Error: -W Warning cannot be negative"
	sys.exit(status_code)

try:
	url = "http://{host}:{port}/{location}".format(host=args.host,port=args.port, location=args.location)
	nginx_stats = urllib2.urlopen(url).read().split('\n')
	metrics[args.metric](nginx_stats)
except KeyError:
	str_metrics =  "Supported Metrics: ["
	for metric in metrics:
		str_metrics += ("'" + metric + "',")
	print str_metrics[:-1] + "]"
	print "Error: Unrecognized/unsupported metric '{_metric}'".format(_metric=args.metric)
	sys.exit(status_code)
except urllib2.URLError:
	print "Error: Connection Refused - Check host and port arguments"
	sys.exit(status_code)

sys.exit(status_code)

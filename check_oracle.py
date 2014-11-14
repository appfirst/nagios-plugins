#!/user/bin/env python
"""
Author: Tony Ling
Executes 'sqlplus' with query and parses the output.
For use with AppFirst collector
Code based off: http://www.oracle-base.com/dba/script.php?category=monitoring&file=cache_hit_ratio.sql

Created on: 8/1/14
"""

import sys
import subprocess
import argparse
import re

# Metrics dictionary keys are -t metric arguments
# Key value is an array that holds 3 values
# Index 0 = sql query for the metric, 1 = script output string, 2 = less/greater for warning checks
metrics ={}
metrics['cache_hit_ratio'] = [("SELECT Round(((Sum(Decode(a.name, 'consistent gets', a.value, 0)) + "
			"Sum(Decode(a.name, 'db block gets', a.value, 0)) - "
			"Sum(Decode(a.name, 'physical reads', a.value, 0))  )/ "
			"(Sum(Decode(a.name, 'consistent gets', a.value, 0)) + "
				"Sum(Decode(a.name, 'db block gets', a.value, 0)))) "
				"*100,2) \"Hit Ratio %\" "
		"FROM   v$sysstat a;"),'Cache Hit Ratio','less']
metrics['connected_users'] = [("SELECT count(*) FROM v$session "
        "WHERE username IS NOT NULL "
        "ORDER BY username ASC;"),'Number of connected users','greater']
metrics['db_block_changes'] = [("SELECT Sum(Decode(a.name, 'db block changes', a.value, 0)) \"DB Block Changes\" "
		"FROM   v$sysstat a;"),'Number of DB Block Changes','less']
metrics['db_block_gets'] = [("SELECT Sum(Decode(a.name, 'db block gets', a.value, 0)) \"DB Block Gets\" "
		"FROM   v$sysstat a;"),'Number of DB Block Gets','less']
metrics['physical_reads'] = [("SELECT Sum(Decode(a.name, 'physical reads', a.value, 0)) \"Physical Reads\" "
		"FROM   v$sysstat a;"),'Disk IO Physical Reads','less']
metrics['physical_writes'] = [("SELECT Sum(Decode(a.name, 'physical writes', a.value, 0)) \"Physical Writes\" "
		"FROM   v$sysstat a;"),'Disk IO Physical Writes','less']
metrics['enqueue_deadlocks'] = [("SELECT VALUE "
		"FROM   v$sysstat a WHERE NAME ='enqueue deadlocks';"),'Enqueue Deadlocks','less']
metrics['enqueue_waits'] = [("SELECT VALUE "
		"FROM   v$sysstat a WHERE NAME ='enqueue waits';"),'Enqueue Waits','less']

status_code = 3

parser = argparse.ArgumentParser()
parser.add_argument('-W', '--warning', help="Warning threshold, triggers if less than or equal to", default=None, type=float)
parser.add_argument('-C', '--critical', help="Critical threshold, triggers if less than or equal to", default=None, type=float)
parser.add_argument('-t', '--metric', help='Metric to choose', default=None, required=True)

args = parser.parse_args()

try:
	query = metrics[args.metric][0]
	msg = metrics[args.metric][1]
	oracle_info = subprocess.Popen("echo {query} | sqlplus / as sysdba".format(query=query),
		 stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
	output, err = oracle_info.communicate()

	oracle_info.wait()
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

counter = 0
value = None
lines = output.split('\n')
for line in lines:
	tokens = line.strip().split('\n')
	if tokens[0]:
		found = re.search('--', tokens[0])
		if found:
			value = float(lines[counter+1].strip())
			break;
	counter += 1

if (value is None):
	print "ERROR - Script Failed, check if sqlplus command is installed"
	sys.exit(status_code)

if (metrics[args.metric][2] == 'less'):
	if (args.critical and float(value) <= args.critical):
		print "CRITICAL - " + msg + ": " + str(value) + "|" + metric + "=" + str(value)
		status_code = 2
	elif (args.warning and float(value) <= args.warning):
		print "WARNING - " + msg + ": " + str(value) + "|" + metric + "=" + str(value)
		status_code = 1
	else:
		print "OK - " + msg + ": " + str(value) + "|" + metric + "=" + str(value)
		status_code = 0
else:
	if (args.critical and float(value) >= args.critical):
		print "CRITICAL - " + msg + ": " + str(value) + "|" + metric + "=" + str(value)
		status_code = 2
	elif (args.warning and float(value) >= args.warning):
		print "WARNING - " + msg + ": " + str(value) + "|" + metric + "=" + str(value)
		status_code = 1
	else:
		print "OK - " + msg + ": " + str(value) + "|" + metric + "=" + str(value)
		status_code = 0
sys.exit(status_code)

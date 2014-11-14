#!/usr/bin/env python
"""
Updated on November 14, 2014 by Tony Ling
Uses rabbitmq's HTTP API to get overview metrics and parses the output.
"""
import argparse
import shlex
import subprocess
import sys
import json
import urllib2

QSTATUS_CMD = "/usr/sbin/rabbitmqctl list_queues -q"

# metrics dictionary keys are script metric arguments, -t
# key is also metric name corresponding to HTTP API response metric
# key value is an array with index 0=HTTP API json response field, 1=script output string
# IE: HTTP API returns nested JSON object with fields and metrics
metrics = {}
metrics['messages_ready'] = ['queue_totals','Number of messages ready']
metrics['messages'] = ['queue_totals','Number of pending messages']
metrics['messages_unacknowledged'] = ['queue_totals','Number of messages unacknowledged']
metrics['channels'] = ['object_totals','Number of channels']
metrics['connections'] = ['object_totals','Number of connections']
metrics['consumers'] = ['object_totals','Number of consumers']
metrics['exchanges'] = ['object_totals','Number of exchanges']
metrics['queues'] = ['object_totals','Number of queues']

def get_metric_value(host, port, username, password, json_field, metric, msg, critical, warning):
	status_code = 3
	passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
	passman.add_password(None, "http://{host}:{port}/api/overview".format(host=host, port=port), username, password)
	urllib2.install_opener(urllib2.build_opener(urllib2.HTTPBasicAuthHandler(passman)))

	req = urllib2.Request("http://{host}:{port}/api/overview".format(host=host, port=port))
	response = urllib2.urlopen(req)
	output = response.read()
	output = json.loads(output)

	# To find all 'json_field' keys in returned HTTPA API output
	#for key in output:
	#	print key

	value = output[json_field][metric]
	if (critical is not None and int(value) >= critical):
		print "CRITICAL - " + msg + ": " + str(value) + "|" + metric + "=" + str(value) 
		status_code = 2
	elif (warning is not None and int(value) >= warning):
		print "WARNING - " + msg + ": " + str(value) + "|" + metric + "=" + str(value) 
		status_code = 1
	else:
		print "OK - " + msg + ": " + str(value)  + "|" + metric + "=" + str(value) 
		status_code = 0
	return status_code

def get_qstatus():
    p = subprocess.Popen(shlex.split(QSTATUS_CMD), stdout=subprocess.PIPE)
    for line in p.stdout:
        yield line.strip()


def check_values(substrs, warning, critical, lines):
    queues_names = []
    queues = []
    total = 0
    num_substrs = len(substrs)
    for line in lines:
        if not line:
            continue
        qname, num_qitems = line.split()
        if len([i for i in substrs if i in qname]) < num_substrs:
            continue
        queues_names.append(qname)
        total += int(num_qitems)
        queues.append((qname, num_qitems))

    queue_status = " ".join("{0}={1}".format(*i) for i in queues)
    msg = "- queues: {0} | qitems={1};{2};{3} {4}".format(
        " ".join(queues_names), total, warning, critical, queue_status)
    if total >= critical:
        status = "CRITICAL"
        ret = 2
    elif total >= warning:
        status = "WARNING"
        ret = 1
    else:
        status = "OK"
        ret = 0
    return "{0} {1}".format(status, msg), ret

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--warning", help='Metric Warning threshold', type=int, required=False)
    parser.add_argument("-c", "--critical", help='Metric Critical threshold', type=int, required=False)
    parser.add_argument('-s', '--substring', help='Queue names, used with \'-t list_queues\'', default = None)
    parser.add_argument('-H', '--host', help='Host location, default=localhost', default='localhost')
    parser.add_argument('-P', '--port', help='Port number, default=6379', default='15672')
    parser.add_argument('-U', '--username', help='Username when connecting to the server, default=guest', default='guest', type=str)
    parser.add_argument('-p', '--password', help='Password when connecting to the server, default=guest', default='guest', type=str)
    parser.add_argument('-t', '--metric', help='Metric to choose', default=None, required=True)
    args = parser.parse_args()

    status_code = 3
    if (args.metric == 'list_queues'):
        ret = 3
        try:
            if (args.substring):
                substrs = args.substring.split(",")
                msg, ret = check_values(
			substrs, args.warning, args.critical, get_qstatus())
            else:
                print '-s or --substring argument required with metric \'list_queues\''
        except:
            msg = "UNKNOWN - exception occured"
            print msg
        sys.exit(ret)

    try:
    	status_code = get_metric_value(args.host, args.port, args.username, args.password,
		 metrics[args.metric][0],args.metric,metrics[args.metric][1], args.critical, args.warning)
    except KeyError:
        print "Error: Unrecognized/unsupported metric '{_metric}'".format(_metric=args.metric)
        str_metrics =  "Supported Metrics: ["
        for metric in metrics:
            str_metrics += ("'" + metric + "',")
        print str_metrics[:-1] + "]"
    except urllib2.URLError:
        print "Error: Connection Refused - Check host and port arguments"
    sys.exit(status_code)

if __name__ == "__main__":
    main()

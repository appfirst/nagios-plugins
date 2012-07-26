import argparse
import shlex
import subprocess
import sys

QSTATUS_CMD = "/usr/sbin/rabbitmqctl list_queues -q"


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
    parser.add_argument("-w", "--warning", type=int, required=True)
    parser.add_argument("-c", "--critical", type=int, required=True)
    parser.add_argument("substring")
    args = parser.parse_args()

    try:
        substrs = args.substring.split(",")
        msg, ret = check_values(
            substrs, args.warning, args.critical, get_qstatus())
    except:
        msg = "UNKNOWN - exception occured"
        ret = 3
    print msg
    sys.exit(ret)


if __name__ == "__main__":
    main()

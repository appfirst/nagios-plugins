#!/usr/bin/env python
import sys
import os
import time
import ConfigParser
import argparse
import logging
from plugins.options import Options
from plugins.apache_url_stat import ApacheLogsParser
from plugins.urls_counter import UrlsCounter
from daemon import runner

LOGGER = logging.getLogger(__name__)


class App():

    def __init__(self, opt = None):

        if opt and opt.interval:
            LOGGER.info('Custom interval is set ' + opt.interval)
            self.interval = int(opt.interval)
        else:
            self.interval = 60 # in sec

        # apacheLogFilePath
        if opt and opt.apacheLogFilePath:
            LOGGER.info('Custom apache log file is set ' + opt.apacheLogFilePath)
            self.apacheLogFilePath = opt.apacheLogFilePath
        else:
            self.apacheLogFilePath = '/var/log/apache2/access.log'

        if opt and opt.outputFilePath:
            self.outputFilePath = opt.outputFilePath
        else:
            scriptPath = os.path.realpath(__file__)
            pathname = os.path.dirname(scriptPath)
            self.outputFilePath = pathname + '/af_apache_visited_urls.log'



        self.parser = ApacheLogsParser(apacheLogFilePath = self.apacheLogFilePath)
        self.urlsCounter = UrlsCounter(self.outputFilePath)

        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.pidfile_path =  '/tmp/af-apache-url-logs.pid'
        self.pidfile_timeout = 1

    def run(self):
        while True:

            LOGGER.info(' parsing apache logs ')
            urls = self.parser.parse()
            if len(urls) > 0:
                self.urlsCounter.update(urls)
                LOGGER.debug(' new urls %d ', len(urls))
            time.sleep(self.interval)


if __name__ == "__main__":
    parser = argparse.ArgumentParser( epilog='use -h/--help to see full help', conflict_handler='resolve')
    opt = Options()

    if len(sys.argv) > 1:

        if (sys.argv[1] == 'start' or sys.argv[1] == 'stop' or sys.argv[1] == 'restart' ):
            config = sys.argv[2:]
        else:
            config = sys.argv[1:]


        # if sys.argv[1] == 'start'
        options = opt.get_options(parser, config = config)
        opt.setup_logger(LOGGER)

        app = App(opt = options)



        # runing daemon
        daemon_runner = runner.DaemonRunner(app)
        daemon_runner.do_action()

    else:
        options = opt.get_options(parser)
        parser.print_help()
        exit()




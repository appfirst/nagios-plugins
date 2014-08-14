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
from plugins.daemon import Daemon
from plugins.app_thread import ProcessThread
from daemon import runner
import socket




LOGGER = logging.getLogger(__name__)

HOSTNAME = '127.0.0.1'
PORT = 30310
tServer = None



class App(Daemon):

    def __init__(self, *args, **kwargs):

        super( App, self ).__init__(*args, **kwargs)
        self._socket = None
        self._tServer = None
        self.running = None
        self.tagsEnabled = None



    def initApp(self, opt = None):

        if opt and opt.interval:
            LOGGER.info('Custom interval is set ' + opt.interval)
            self.interval = int(opt.interval)
        else:
            self.interval = 60 # in sec

        # apacheLogFilePath
        if opt and opt.apacheLogFilePath:
            LOGGER.info('Custom apache log file is set ' + opt.apacheLogFilePath)
            files = opt.apacheLogFilePath.split(',')
            self.apacheLogFilePath = files
        else:
            self.apacheLogFilePath = ['/var/log/apache2/access.log']

        if opt and opt.outputFilePath:
            self.outputFilePath = opt.outputFilePath
        else:
            scriptPath = os.path.realpath(__file__)
            pathname = os.path.dirname(scriptPath)
            self.outputFilePath = pathname + '/af_apache_visited_urls.log'

        if opt and opt.tags:
            self.tagsEnabled = opt.tags


        self.parser = ApacheLogsParser(apacheLogFilePath = self.apacheLogFilePath)
        self.urlsCounter = UrlsCounter(self.outputFilePath, tags = self.tagsEnabled)


    def stop(self):

        if self._tServer is not None:
            LOGGER.debug('stopping sockets thread')
            self._tServer.stop()

        super( App, self ).stop()


    def run(self):

        if self.running is None:
            self.running = True

            i = 0
            self.urlsLength = 0

            if self._tServer is None:
                self._tServer = ProcessThread(host = HOSTNAME, port = PORT)
                self._tServer.start()
                self._tServer.setData(0)

            while True:

                if i >= self.interval:
                    LOGGER.debug (' parsing apache logs ')
                    urls = self.parser.parse()
                    self.urlsLength = len(urls)
                    i = 0
                    if self.urlsLength > 0:
                        self.urlsCounter.update(urls)
                        self.isDataPolled = False
                        LOGGER.debug(' new urls %d ', len(urls))
                        # if tread is running
                        if self._tServer is not None:
                            self._tServer.setData(self.urlsLength)

                # LOGGER.debug(' --- {i} {n}'.format(i=i,n=self.interval))
                time.sleep(1)
                i = i + 1
        else:
            LOGGER.debug (' application already running')


    def status(self):
        LOGGER.debug (self.urlsLength)


if __name__ == '__main__':
    parser = argparse.ArgumentParser( epilog='use -h/--help to see full help', conflict_handler='resolve')
    opt = Options()

    if len(sys.argv) > 1:

        if (sys.argv[1] == 'start' or sys.argv[1] == 'stop' or sys.argv[1] == 'restart' or sys.argv[1] == 'status'):
            config = sys.argv[2:]
        else:
            config = sys.argv[1:]

        options = opt.get_options(parser, config = config)
        opt.setup_logger(LOGGER)



        if sys.argv[1] == 'status':
            try:
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                LOGGER.debug('#connecting {h} {p}...'.format(p = PORT, h = HOSTNAME))
                client.connect((HOSTNAME, PORT))
                client.send('ping')

                LOGGER.debug('#reciving data...')
                data = client.recv(512)
                LOGGER.debug('#ok: {d}'.format(d = data))

                client.shutdown(socket.SHUT_RDWR)
                client.close()
                # PING ok - Packet loss = 0%, RTA = 0.80 ms | percent_packet_loss=0, rta=0.80
                if (data == '-1'):
                    print('AF.APACHE.URLS.COUNTER ok')
                else:
                    print ('AF.APACHE.URLS.COUNTER ok - urls count = ' + data + ' | urls_count=' + data)
            except Exception as msg:
                print 'AF.APACHE.URLS.COUNTER CRITICAL - daemon not runining'
                LOGGER.debug (msg)
            exit(0)


        else:
            daemon = App('/tmp/af-apache-url-logs.pid', stdout='/dev/console', stderr='/dev/console')
            if 'start' == sys.argv[1]:
                daemon.initApp(opt = options)
                daemon.start()
            elif 'stop' == sys.argv[1]:
                print 'stopping...'
                daemon.stop()
                print 'ok'
            elif 'restart' == sys.argv[1]:
                daemon.restart()
            else:
                print 'Unknown command'
                sys.exit(2)
            sys.exit(0)


    else:
        options = opt.get_options(parser)
        parser.print_help()
        exit()






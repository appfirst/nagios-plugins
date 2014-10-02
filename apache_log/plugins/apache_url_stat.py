#!/usr/bin/env python
import sys
import logging
import os
import re

LOGGER = logging.getLogger(__name__)


class ApacheLogsParser():

    def __init__(self, apacheLogFilePath = None):
        logging.info('creating ApacheLogsParser')
        self.lastModifyed = 0
        self.lastLine = 0
        self.created = None

        if apacheLogFilePath is None:
            LOGGER.critical('apache logs file not defined')

        self.apacheLogFilePath = apacheLogFilePath

    def load_log_file(self, filename, line = 0):
        data = None
        f = None
        if os.path.isfile(filename):
            try:
                LOGGER.debug('reading log file ' + filename)
                lm = os.path.getmtime(filename)

                LOGGER.debug('checking last modification of a file ' + filename + ' ' + str(lm))
                if lm > self.lastModifyed:
                    f = file(filename, 'r')
                    lines = f.readlines()
                    currentLinesNumber = len(lines)

                    if (currentLinesNumber < self.lastLine):
                        LOGGER.debug('reseting last line number from ' + str(self.lastLine) + ' to 0')
                        self.lastLine = 0

                    LOGGER.debug('total records in apache log file ' + str(currentLinesNumber))
                    LOGGER.debug('last parsed record(line) ' + str(self.lastLine))
                    if currentLinesNumber > self.lastLine:
                        data = lines[self.lastLine : currentLinesNumber]
                        self.lastLine = len(lines)
                    self.lastModifyed = lm
                else:
                    data = []
            finally:
                if f is not None:
                    f.close()

        return data

    def parse(self):
        urls = []
        logsList = []
        try:
            for logFile in self.apacheLogFilePath:
                log = self.load_log_file(logFile)
                if log is not None:
                    logsList.extend( log )

            if logsList is not None:
                for line in logsList:
                    url = map(';'.join, re.findall(r'([(\d\.)]+) - - (.*?) "(.*?)"', line))

                    if len(url) > 0:
                        a = url[0].split(';')
                        u = a[2].split(' ')
                        obj = {'date': a[1], 'url': u[1]}
                        urls.append(obj)
                        # LOGGER.debug(obj)
                    else:
                        logging.info('no new urls was found')
            else:
                LOGGER.critical('apache log file is empty')
                # LOGGER.debug(log)
        except Exception as e:
            LOGGER.critical('Serious Error occured: %s', e)

        return urls


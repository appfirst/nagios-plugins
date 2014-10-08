#!/usr/bin/env python
import sys
import logging
import os
import re
import threading
import pickle


LOGGER = logging.getLogger(__name__)


class StatsdSender(threading.Thread):

    def __init__(self, apacheHostName = None, pklData = None):
        super(StatsdSender, self).__init__()

        LOGGER.debug('init StatsdSender')


        self.urlsSumm = None
        self.urls = None
        self.pklData = pklData

        try:
            if self.pklData is None:
                pklFile = open('/tmp/data.pkl', 'rb')
                self.pklData = pickle.load(pklFile)
                pklFile.close()

                LOGGER.info('reading pickle data')

            if self.pklData is not None:

                self.urlsSumm = self.pklData['urlsSumm']
                self.urls = self.pklData['urls']


        except Exception as e:
            LOGGER.critical('Serious Error occured: %s', e)

        self.running = True
        self.stoprequest = threading.Event()
        LOGGER.info('creating StatsdSender')
        self.apacheHostName = apacheHostName


    def getBaseName(self):
        name = ''
        if self.apacheHostName is not None:
            name = self.apacheHostName + '.'

        return name

    def convertUrlToName(self, url):

        url = url.replace ('http://', '')
        url = url.replace ('https://', '')
        url = url.replace (' ', '')
        index = url.find('?')
        if index > 0:
            url = url[0:index]

        if url[0] is '/':
            url = url[1:]
        return url

    def increment(self, statsd, name, val):

        while val > 0:
            statsd.increment(name)
            val = val - 1

    def sendCountOfUrls(self, Statsd, urls):

        LOGGER.debug('sendCountOfUrls')

        for key, val in urls.iteritems():
            if key is not '*':
                name = elf.getBaseName() + self.convertUrlToName(key)
                LOGGER.debug('converting url ' + key + ' to counter name ' + name)
                LOGGER.debug('setting counter ' + name + ' to %d' %  val['count'])
                self.increment(Statsd, name, val['count'])

    def sendSummOfUrls(self, Statsd, urls):
        name = self.getBaseName()
        Statsd.gauge('af_url_counter.' + name, len(urls))

    def run(self):

        try:

            LOGGER.debug('run StatsdSender')
            from afstatsd import Statsd, AFTransport
            # Statsd.set_transport(AFTransport(logger=LOGGER, verbosity=True))

            if self.urlsSumm is not None:
                self.sendCountOfUrls(Statsd, self.urlsSumm)

            if self.urls is not None:
                self.sendSummOfUrls(Statsd, self.urls)

            if self.isAlive():
                LOGGER.debug('statsD thread NOT stoped')
            else:
                LOGGER.debug('statsD thread stoped')

        except Exception as e:
            LOGGER.critical('Serious Error occured: %s', e)


    def join(self, timeout=None):
        self.stoprequest.set()
        self.running = None
        super(StatsdSender, self).join(timeout)




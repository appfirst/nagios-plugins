#!/usr/bin/env python
import sys
import logging
import os
import re
from threading import Thread
from afstatsd import Statsd, AFTransport
import pickle


LOGGER = logging.getLogger(__name__)


class StatsdSender(Thread):

    def __init__(self, apacheHostName = None):
        super(StatsdSender, self).__init__()
        self.urlsSumm = None
        self.urls = None

        try:
            pklFile = open('/tmp/data.pkl', 'rb')
            pklData = pickle.load(pklFile)

            LOGGER.info('reading pickle data')
            LOGGER.info(pklData)
            if pklData is not None:

                self.urlsSumm = pklData['urlsSumm']
                self.urls = pklData['urls']

            pklFile.close()
        except Exception as e:
            LOGGER.critical('Serious Error occured: %s', e)

        self.running = True
        LOGGER.info('creating StatsdSender')
        self.apacheHostName = apacheHostName


    def getBaseName(self):
        name = 'af_url_counter'
        if self.apacheHostName is not None:
            name = name + '.' + self.apacheHostName

        return name

    def convertUrlToName(self, url):

        # LOGGER.debug('convertUrlToName ' + url)
        url = url.replace ('http://', '')
        url = url.replace ('https://', '')
        url = url.replace ('/', '_')
        url = url.replace (' ', '')
        index = url.find('?')
        if index > 0:
            url = url[0:index]
        return url

    def sendCountOfUrls(self, urls):

        LOGGER.debug('sendCountOfUrls')

        for key, val in urls.iteritems():
            if key is not '*':
                name = self.getBaseName() + '.' + self.convertUrlToName(key)
                LOGGER.debug('converting url ' + key + ' to counter name ' + name)
                LOGGER.debug('setting gauge ' + name + ' to %d' %  val['count'])
                Statsd.gauge(name, val['count'])

    def sendSummOfUrls(self, urls):
        name = self.getBaseName()
        Statsd.gauge(name, len(urls))

    def run(self):
        LOGGER.debug('run StatsdSender')
        # Statsd.set_transport(AFTransport(logger=LOGGER))
        if self.urlsSumm is not None:
            self.sendCountOfUrls(self.urlsSumm)

        if self.urls is not None:
            self.sendSummOfUrls(self.urls)

    def stop(self):

        LOGGER.debug('trying to stop thread')
        if self.running is not None:
            self.running = None
            self.stop()




#!/usr/bin/env python
import sys
import logging
import os
import re

LOGGER = logging.getLogger(__name__)

class UrlsCounter():

    def __init__(self, outputFilePath, tags = None, statsdPrefix = 'apache_url_counter'):
        logging.debug('creating UrlsCounter to file ' + outputFilePath)
        self.outputFilePath = outputFilePath
        self.check_output_file()
        self.statsdPrefix = statsdPrefix

        self.tagsEnabled = tags

    def check_output_file(self):
        if not os.path.isfile(self.outputFilePath):
            f = file(self.outputFilePath, 'w')
            f.close()

    def stringFormatter(self, item, url):
        tag = ''
        if self.tagsEnabled:
            if len(self.tagsEnabled) > 1:
                tag = self.tagsEnabled
            else:
                tag = ':AF_UrlRequestCount:'
        return tag + ' [' + item['date'] + '] ' + str(item['count']) + ' - ' + url + os.linesep

    def append_to_file(self, urls):
        logging.debug('uppending to file ' + self.outputFilePath)
        if len(urls) > 0:
            try:
                f = file(self.outputFilePath, 'a')
                for url in urls:
                    s = self.stringFormatter(urls[url], url);
                    #LOGGER.info(s)
                    f.write(s)

                f.close()
            except Exception as e:
                LOGGER.critical('Serious Error occured: %s', e)



    def update(self, urls):
        urlsCount = {}
	logging.debug('updating to file ' + self.outputFilePath)
        if len(urls) > 0:

            for url in urls:
                if not url['url'] in urlsCount.keys():
                    urlsCount[url['url']] = {'date': url['date'], 'count': 1}
                else:
                    urlsCount[url['url']]['date'] = url['date']
                    urlsCount[url['url']]['count'] += 1


            self.append_to_file(urlsCount)
        return urlsCount


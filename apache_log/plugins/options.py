#!/usr/bin/env python
'''
Options

'''
import sys
import logging
import os
import ConfigParser
import argparse


LOGGER = logging.getLogger(__name__)


class Options(object):

    def __init__(self):
        self.options = None

    def setup_logger(self, logger):
        # ch = logging.StreamHandler()
        level = logging.ERROR
        fh = logging.FileHandler('af-apache-log-daemon.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        # ch.setFormatter(formatter)
        fh.setFormatter(formatter)

        if self.options is not None and self.options.verbose is not None:
            level = self.options.verbose

        # print ('set log level to %d ' % level)
        logger.setLevel(level)

        logger_components = [logger]
        logger_components.append(LOGGER)
        logger_components.append(logging.getLogger(name='plugins.apache_url_stat'))
        #logger_components.append(logging.getLogger(name='plugins.urls_counter'))
        logger_components.append(logging.getLogger(name='plugins.app_thread'))
        logger_components.append(logging.getLogger(name='plugins.statsd_sender'))
        logger_components.append(logging.getLogger(name='plugins.urls_counter'))

        for l in logger_components:
            # l.addHandler(ch)
            if fh:
                l.addHandler(fh)
                l.setLevel(level)


    def get_options(self, parser, config = None):

        parser.add_argument('-v','--verbose', dest='verbose', action='count',default=2, help='Set log level higher you can add multiple')
        parser.add_argument('-V','--very_verbose', dest='verbose', action='store_const', const=4, help='Set log level to highest level of detail')
        parser.add_argument('-f','--log-to-file', dest='logToFile', help='Store output log to file')
        parser.add_argument('-i','--interval', dest='interval', help='Set interval in seconds to run')
        parser.add_argument('-t','--tags', dest='tags', help='Enable tags for log file, should be in format like :AF_TAG_NAME:')
        parser.add_argument('-a','--apache-host', dest='apacheHostName', help='Apache hostname will be included in statsD counter name')
        parser.add_argument('-l','--apache-log-file-path', dest='apacheLogFilePath', help='Path to apache log file')
        parser.add_argument('-o','--output-log-file-path', dest='outputFilePath', help='Path to file where urls count will be saved')


        if config is None:
            options = parser.parse_args()
        else:
            options = parser.parse_args(config)

        level = {
            1: logging.ERROR,
            2: logging.WARNING,
            3: logging.INFO,
            4: logging.DEBUG
        }.get(options.verbose, logging.ERROR)
        options.verbose = level

        self.options = options

        return options

    #def __init__(self):
        # logging.info('creating logger')


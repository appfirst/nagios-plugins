package com.objectstyle.appfirst.jmx.collector.config.parser;

import com.objectstyle.appfirst.jmx.collector.config.CommandLineParserException;

public interface CommandLineParser {
    void parse(String commandLine) throws CommandLineParserException;
}

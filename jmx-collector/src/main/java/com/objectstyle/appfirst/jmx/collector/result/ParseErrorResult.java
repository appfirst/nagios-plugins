package com.objectstyle.appfirst.jmx.collector.result;

import com.objectstyle.appfirst.jmx.collector.config.CommandLineParserException;

public class ParseErrorResult extends Result {
    public ParseErrorResult(CommandLineParserException exception) {
        super("JMX-Collector-Parser", ResultStatus.EXECUTION_ERROR, new ErrorResultData(exception.getMessage()));
    }
}

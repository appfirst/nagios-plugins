package com.objectstyle.appfirst.jmx.collector.config;

public class ThresholdValidationException extends CommandValidationException {
    public ThresholdValidationException() {
        super("Error in threshold definition");
    }
}

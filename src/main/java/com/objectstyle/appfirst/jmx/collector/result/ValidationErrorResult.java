package com.objectstyle.appfirst.jmx.collector.result;

import com.objectstyle.appfirst.jmx.collector.config.CommandValidationException;

public class ValidationErrorResult extends Result {
    public ValidationErrorResult(CommandValidationException exception) {
        super(exception.getMessage(), ResultStatus.EXECUTION_ERROR, new NoResultData());
    }
}

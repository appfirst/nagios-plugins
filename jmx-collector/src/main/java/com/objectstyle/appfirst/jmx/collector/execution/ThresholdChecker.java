package com.objectstyle.appfirst.jmx.collector.execution;

import com.objectstyle.appfirst.jmx.collector.command.ThresholdDefinition;
import com.objectstyle.appfirst.jmx.collector.result.ResultData;

public interface ThresholdChecker {
    boolean checkReached(ThresholdDefinition thresholdDefinition, ResultData resultData);
}

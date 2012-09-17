package com.objectstyle.appfirst.jmx.collector.execution;

import com.objectstyle.appfirst.jmx.collector.command.NoThresholdDefinition;
import com.objectstyle.appfirst.jmx.collector.command.ThresholdDefinition;
import com.objectstyle.appfirst.jmx.collector.result.ResultData;

public class DelegatingThresholdChecker implements ThresholdChecker {
    private final RangeThresholdChecker rangeThresholdChecker = new RangeThresholdChecker();

    @Override
    public boolean checkReached(ThresholdDefinition thresholdDefinition, ResultData resultData) {
        if (thresholdDefinition instanceof NoThresholdDefinition) {
            return false;
        }
        return rangeThresholdChecker.checkReached(thresholdDefinition, resultData);
    }
}

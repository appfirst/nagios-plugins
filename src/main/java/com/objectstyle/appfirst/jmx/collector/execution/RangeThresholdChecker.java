package com.objectstyle.appfirst.jmx.collector.execution;

import com.objectstyle.appfirst.jmx.collector.command.RangeThresholdDefinition;
import com.objectstyle.appfirst.jmx.collector.command.ThresholdDefinition;
import com.objectstyle.appfirst.jmx.collector.result.ResultData;
import com.objectstyle.appfirst.jmx.collector.result.SimpleResultData;

public class RangeThresholdChecker implements ThresholdChecker {
    @Override
    public boolean checkReached(ThresholdDefinition thresholdDefinition, ResultData resultData) {
        if (!(thresholdDefinition instanceof RangeThresholdDefinition)) {
            throw new IllegalArgumentException("Only range thresholds are supported");
        }
        RangeThresholdDefinition rangeThresholdDefinition = (RangeThresholdDefinition) thresholdDefinition;
        if (resultData instanceof SimpleResultData) {
            try {
                long value = Long.valueOf(((SimpleResultData) resultData).getValue());
                if (rangeThresholdDefinition.isInside()) {
                    return rangeThresholdDefinition.getLeftBorder() <= value
                            && rangeThresholdDefinition.getRightBorder() >= value;
                } else {
                    return rangeThresholdDefinition.getLeftBorder() > value
                            || rangeThresholdDefinition.getRightBorder() < value;
                }
            } catch (NumberFormatException e) {
                // non numerical data, ignoring exception
            }
        }
        return false;
    }
}

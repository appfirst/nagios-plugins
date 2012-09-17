package com.objectstyle.appfirst.jmx.collector.config;

import com.objectstyle.appfirst.jmx.collector.command.NoThresholdDefinition;
import com.objectstyle.appfirst.jmx.collector.command.RangeThresholdDefinition;
import com.objectstyle.appfirst.jmx.collector.command.ThresholdDefinition;

public class ThresholdBuilder {
    public ThresholdDefinition fromString(String valueString) throws ThresholdValidationException {
        if (valueString == null || valueString.isEmpty()) {
            return new NoThresholdDefinition();
        }

        boolean inside = false;
        if (valueString.startsWith("@")) {
            inside = true;
            valueString = valueString.substring(1);
        }

        long leftRange;
        long rightRange;
        String[] rangeStrings = valueString.split(":");
        if (rangeStrings.length == 2 || valueString.endsWith(":")) {
            String leftString = rangeStrings[0];
            String rightString = rangeStrings.length == 2 ? rangeStrings[1] : "";
            if (leftString.isEmpty()) {
                throw new ThresholdValidationException();
            }
            leftRange = leftString.equals("~") ? Long.MIN_VALUE : Long.valueOf(leftString);
            rightRange = rightString.equals("~") || rightString.isEmpty() ? Long.MAX_VALUE : Long.valueOf(rightString);
        } else if (rangeStrings.length == 1) {
            leftRange = 0;
            String rightString = rangeStrings[0];
            if (rightString.isEmpty()) {
                throw new ThresholdValidationException();
            }
            rightRange = rightString.equals("~") ? Long.MAX_VALUE : Long.valueOf(rightString);
        } else {
            throw new ThresholdValidationException();
        }

        return new RangeThresholdDefinition(leftRange, rightRange, inside);
    }
}

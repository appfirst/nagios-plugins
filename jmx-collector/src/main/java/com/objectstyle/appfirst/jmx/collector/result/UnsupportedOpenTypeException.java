package com.objectstyle.appfirst.jmx.collector.result;

import javax.management.openmbean.OpenType;

public class UnsupportedOpenTypeException extends UnsupportedDataTypeException {
    public UnsupportedOpenTypeException(OpenType<?> type) {
        super(type.getTypeName());
    }
}

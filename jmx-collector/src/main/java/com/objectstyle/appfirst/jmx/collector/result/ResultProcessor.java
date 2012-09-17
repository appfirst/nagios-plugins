package com.objectstyle.appfirst.jmx.collector.result;

import javax.management.MBeanAttributeInfo;
import javax.management.openmbean.OpenType;

public interface ResultProcessor {
    void startResult(String outputName);

    void startExecutionError(String executionErrorMessage);

    void startData(MBeanAttributeInfo attributeInfo, Object value) throws UnsupportedDataTypeException;

    <T> void startOpenMBeanData(OpenType<T> type, T value) throws UnsupportedOpenTypeException;

    void endResult();
}

package com.objectstyle.appfirst.jmx.collector.result;

public interface MBeanDataConverter<T, V> {
    ResultData convert(T type, V value) throws UnsupportedDataTypeException;
}
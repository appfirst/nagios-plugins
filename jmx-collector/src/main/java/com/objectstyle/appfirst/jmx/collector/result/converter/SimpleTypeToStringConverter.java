package com.objectstyle.appfirst.jmx.collector.result.converter;

class SimpleTypeToStringConverter<T> {
    String convert(T value) {
        return value.toString();
    }
}

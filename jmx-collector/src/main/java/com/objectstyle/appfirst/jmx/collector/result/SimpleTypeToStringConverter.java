package com.objectstyle.appfirst.jmx.collector.result;

class SimpleTypeToStringConverter<T> {
    String convert(T value) {
        return value.toString();
    }
}

package com.objectstyle.appfirst.jmx.collector.result;

import com.objectstyle.appfirst.jmx.collector.result.converter.ArrayTypeConverter;
import com.objectstyle.appfirst.jmx.collector.result.converter.CompositeTypeConverter;
import com.objectstyle.appfirst.jmx.collector.result.converter.SimpleTypeConverter;

import javax.management.openmbean.ArrayType;
import javax.management.openmbean.CompositeType;
import javax.management.openmbean.OpenType;
import javax.management.openmbean.SimpleType;

public enum OpenMBeanDataConverterFactory {
    INSTANCE;

    @SuppressWarnings("unchecked")
    public OpenMBeanDataConverter getConverter(OpenType<?> type)
            throws UnsupportedOpenTypeException {
        if (type instanceof ArrayType<?>) {
            return new ArrayTypeConverter();
        } else if (type instanceof SimpleType<?>) {
            return new SimpleTypeConverter();
        } else if (type instanceof CompositeType) {
            return new CompositeTypeConverter();
        } else {
            throw new UnsupportedOpenTypeException(type);
        }
    }
}

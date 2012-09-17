package com.objectstyle.appfirst.jmx.collector.result;

import com.google.common.base.Function;

import javax.annotation.Nullable;
import javax.management.openmbean.ArrayType;
import javax.management.openmbean.SimpleType;

import static com.google.common.collect.Lists.newArrayList;
import static com.google.common.collect.Lists.transform;

public class ArrayTypeConverter<T> implements OpenMBeanDataConverter<ArrayType<T[]>, T[]> {
    private SimpleTypeToStringConverter<T> toStringConverter = new SimpleTypeToStringConverter<T>();

    @Override
    public ResultData convert(final ArrayType<T[]> type, T[] values) throws UnsupportedOpenTypeException {
        // only one dimension simple type arrays are supported
        if (!(type.getElementOpenType() instanceof SimpleType) || type.getDimension() != 1) {
            throw new UnsupportedOpenTypeException(type.getElementOpenType());
        }
        return new ArrayResultData("val", transform(newArrayList(values), new Function<T, String>() {
            @Override
            public String apply(@Nullable T input) {
                return toStringConverter.convert(input);
            }
        }));
    }
}

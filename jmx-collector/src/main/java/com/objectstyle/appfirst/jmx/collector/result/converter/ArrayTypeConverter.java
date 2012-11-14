package com.objectstyle.appfirst.jmx.collector.result.converter;

import com.google.common.base.Function;
import com.objectstyle.appfirst.jmx.collector.result.ArrayResultData;
import com.objectstyle.appfirst.jmx.collector.result.OpenMBeanDataConverter;
import com.objectstyle.appfirst.jmx.collector.result.ResultData;
import com.objectstyle.appfirst.jmx.collector.result.SimpleResultData;
import com.objectstyle.appfirst.jmx.collector.result.UnsupportedOpenTypeException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import javax.annotation.Nullable;
import javax.management.openmbean.ArrayType;
import javax.management.openmbean.SimpleType;

import static com.google.common.collect.Lists.newArrayList;
import static com.google.common.collect.Lists.transform;
import static java.lang.String.format;

public class ArrayTypeConverter<T> implements OpenMBeanDataConverter<ArrayType<T[]>, T[]> {
    private static final Logger LOGGER = LoggerFactory.getLogger(CompositeTypeConverter.class);

    private SimpleTypeToStringConverter<T> toStringConverter = new SimpleTypeToStringConverter<T>();

    @Override
    public ResultData convert(final ArrayType<T[]> type, T[] values) throws UnsupportedOpenTypeException {
        if (!(type.getElementOpenType() instanceof SimpleType)) {
            LOGGER.warn(format("Unsupported data type '%s' inside ArrayType bean.", type.getElementOpenType()));
        }
        return new ArrayResultData(SimpleResultData.DEFAULT_KEY, transform(newArrayList(values), new Function<T, String>() {
            @Override
            public String apply(@Nullable T input) {
                return toStringConverter.convert(input);
            }
        }));
    }
}

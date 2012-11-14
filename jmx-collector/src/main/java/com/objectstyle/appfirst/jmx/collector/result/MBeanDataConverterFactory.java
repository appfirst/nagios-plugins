package com.objectstyle.appfirst.jmx.collector.result;

import com.objectstyle.appfirst.jmx.collector.result.converter.CompositeTypeConverter;
import com.objectstyle.appfirst.jmx.collector.result.converter.MapConverter;
import com.objectstyle.appfirst.jmx.collector.result.converter.SetConverter;
import com.objectstyle.appfirst.jmx.collector.result.converter.ToStringConverter;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Map;
import java.util.Set;

import static java.lang.String.format;

public enum MBeanDataConverterFactory {
    INSTANCE;

    private static final Logger LOGGER = LoggerFactory.getLogger(CompositeTypeConverter.class);

    @SuppressWarnings("unchecked")
    public MBeanDataConverter getConverter(String typeClassName) throws UnsupportedDataTypeException {

        if (Primitives.isPrimitiveOrWrapperType(classForName(typeClassName))) {
            LOGGER.debug(format("Converting result from primitive '%s' type", typeClassName));
            return new ToStringConverter();
        }
        else if (typeClassName.equals(Map.class.getName())) {
            LOGGER.debug(format("Converting result from '%s' type", typeClassName));
            return new MapConverter();
        }
        else if (typeClassName.equals(Set.class.getName())) {
            LOGGER.debug(format("Converting result from '%s' type", typeClassName));
            return new SetConverter();
        }
        else {
            throw new UnsupportedDataTypeException(format("Unsupported data type '%s'", typeClassName));
        }
    }

    private Class<?> classForName(String fullyQualifiedClassName) throws UnsupportedDataTypeException {
        try {
            return Class.forName(fullyQualifiedClassName);
        }
        catch (ClassNotFoundException e) {
            if (fullyQualifiedClassName.equals("int")) {
                return int.class;
            }
            else if (fullyQualifiedClassName.equals("boolean")) {
                return boolean.class;

            }
            else if (fullyQualifiedClassName.equals("char")) {
                return char.class;

            }
            else if (fullyQualifiedClassName.equals("byte")) {
                return byte.class;

            }
            else if (fullyQualifiedClassName.equals("short")) {
                return short.class;

            }
            else if (fullyQualifiedClassName.equals("double")) {
                return double.class;

            }
            else if (fullyQualifiedClassName.equals("long")) {
                return long.class;

            }
            else if (fullyQualifiedClassName.equals("boolean")) {
                return boolean.class;

            }
            else if (fullyQualifiedClassName.equals("void")) {
                return void.class;

            }
            else if (fullyQualifiedClassName.equals("float")) {
                return float.class;

            }
            throw new UnsupportedDataTypeException(fullyQualifiedClassName);
        }
    }
}
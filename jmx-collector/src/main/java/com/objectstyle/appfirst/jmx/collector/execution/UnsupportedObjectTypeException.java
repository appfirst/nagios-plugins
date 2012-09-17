package com.objectstyle.appfirst.jmx.collector.execution;

import com.objectstyle.appfirst.jmx.collector.command.ValueDefinition;

public class UnsupportedObjectTypeException extends CommandExecutionException {
    public UnsupportedObjectTypeException(ValueDefinition valueDefinition, Class<?> objectType) {
        super(String.format("Unsupported object type '%s' for attribute '%s' of object '%s'",
                objectType.getName(), valueDefinition.getAttribute(), valueDefinition.getName()));
    }
}

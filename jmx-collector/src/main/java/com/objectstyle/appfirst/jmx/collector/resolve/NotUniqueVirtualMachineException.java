package com.objectstyle.appfirst.jmx.collector.resolve;

import com.objectstyle.appfirst.jmx.collector.command.VirtualMachineDefinition;

import static java.lang.String.format;

public class NotUniqueVirtualMachineException extends VirtualMachineResolverException {
    public NotUniqueVirtualMachineException(VirtualMachineDefinition definition) {
        super(format("Virtual machine definition matches more then one virtual machine: '%s'", definition.toString()));
    }
}

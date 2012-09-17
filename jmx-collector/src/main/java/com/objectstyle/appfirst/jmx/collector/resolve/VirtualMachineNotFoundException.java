package com.objectstyle.appfirst.jmx.collector.resolve;

import com.objectstyle.appfirst.jmx.collector.command.VirtualMachineDefinition;

import static java.lang.String.format;

public class VirtualMachineNotFoundException extends VirtualMachineResolverException {
    public VirtualMachineNotFoundException(VirtualMachineDefinition definition) {
        super(format("Virtual machine definition does not match any virtual machine: '%s'", definition.toString()));
    }
}

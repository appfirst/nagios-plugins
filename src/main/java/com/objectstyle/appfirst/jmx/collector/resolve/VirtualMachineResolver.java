package com.objectstyle.appfirst.jmx.collector.resolve;

import com.objectstyle.appfirst.jmx.collector.command.VirtualMachineDefinition;

public interface VirtualMachineResolver {
    VirtualMachineIdentifier resolve(VirtualMachineDefinition definition) throws VirtualMachineResolverException;
}

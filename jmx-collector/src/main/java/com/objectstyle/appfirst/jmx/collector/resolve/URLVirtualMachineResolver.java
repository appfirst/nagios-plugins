package com.objectstyle.appfirst.jmx.collector.resolve;

import com.objectstyle.appfirst.jmx.collector.command.URLVirtualMachineDefinition;
import com.objectstyle.appfirst.jmx.collector.command.VirtualMachineDefinition;

public class URLVirtualMachineResolver implements VirtualMachineResolver {
    @Override
    public VirtualMachineIdentifier resolve(VirtualMachineDefinition definition)
            throws VirtualMachineResolverException {
        if (definition instanceof URLVirtualMachineDefinition) {
            return new VirtualMachineIdentifier(((URLVirtualMachineDefinition) definition).getUrl());
        }
        throw new IllegalArgumentException("URL resolver supports URL definitions only");
    }
}

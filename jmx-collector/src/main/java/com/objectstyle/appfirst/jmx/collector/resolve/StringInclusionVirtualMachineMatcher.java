package com.objectstyle.appfirst.jmx.collector.resolve;

import com.objectstyle.appfirst.jmx.collector.command.PatternVirtualMachineDefinition;
import com.objectstyle.appfirst.jmx.collector.command.VirtualMachineDefinition;
import com.sun.tools.attach.VirtualMachineDescriptor;

public abstract class StringInclusionVirtualMachineMatcher implements VirtualMachineMatcher {
    protected abstract String getVirtualMachineString(VirtualMachineDescriptor descriptor);

    @Override
    public boolean matches(VirtualMachineDefinition definition, VirtualMachineDescriptor descriptor) {
        if (definition instanceof PatternVirtualMachineDefinition) {
            return getVirtualMachineString(descriptor)
                    .contains(((PatternVirtualMachineDefinition) definition).getMatchPattern());
        }
        return false;
    }
}

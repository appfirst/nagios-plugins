package com.objectstyle.appfirst.jmx.collector.resolve;

import com.objectstyle.appfirst.jmx.collector.command.VirtualMachineDefinition;
import com.sun.tools.attach.VirtualMachineDescriptor;

public interface VirtualMachineMatcher {
    boolean matches(VirtualMachineDefinition definition, VirtualMachineDescriptor descriptor);
}

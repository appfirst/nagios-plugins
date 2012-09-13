package com.objectstyle.appfirst.jmx.collector.resolve;

import com.google.common.base.Objects;
import com.sun.tools.attach.VirtualMachineDescriptor;

import javax.management.remote.JMXServiceURL;

public class LocalVirtualMachineIdentifier extends VirtualMachineIdentifier {
    private final VirtualMachineDescriptor descriptor;

    public LocalVirtualMachineIdentifier(VirtualMachineDescriptor descriptor, JMXServiceURL url) {
        super(url);
        this.descriptor = descriptor;
    }

    public VirtualMachineDescriptor getDescriptor() {
        return descriptor;
    }

    @Override
    public String toString() {
        return Objects.toStringHelper(this)
                .add("url", getUrl())
                .add("descriptor", getDescriptor())
                .toString();
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof LocalVirtualMachineIdentifier)) return false;
        if (!super.equals(o)) return false;

        LocalVirtualMachineIdentifier that = (LocalVirtualMachineIdentifier) o;

        return descriptor.equals(that.descriptor);
    }

    @Override
    public int hashCode() {
        int result = super.hashCode();
        result = 31 * result + (descriptor != null ? descriptor.hashCode() : 0);
        return result;
    }
}

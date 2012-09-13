package com.objectstyle.appfirst.jmx.collector.resolve;

import com.google.common.base.Objects;

import javax.management.remote.JMXServiceURL;
import java.util.ArrayList;
import java.util.List;

public class VirtualMachineIdentifier {
    private List<VirtualMachineIdentifierInvalidationListener> listeners;

    private final JMXServiceURL url;

    public VirtualMachineIdentifier(JMXServiceURL url) {
        this.url = url;
        listeners = new ArrayList<VirtualMachineIdentifierInvalidationListener>();
    }

    public JMXServiceURL getUrl() {
        return url;
    }

    public void invalidate() {
        for (VirtualMachineIdentifierInvalidationListener listener : listeners) {
            listener.identifierInvalidated(this);
        }
    }

    public void addInvalidationListener(VirtualMachineIdentifierInvalidationListener listener) {
        if (!listeners.contains(listener)) {
            listeners.add(listener);
        }
    }

    @Override
    public String toString() {
        return Objects.toStringHelper(this)
                .add("url", getUrl())
                .toString();
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;

        VirtualMachineIdentifier that = (VirtualMachineIdentifier) o;

        return url.equals(that.url);
    }

    @Override
    public int hashCode() {
        return url != null ? url.hashCode() : 0;
    }
}

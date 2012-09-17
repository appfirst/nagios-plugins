package com.objectstyle.appfirst.jmx.collector.command;

import com.google.common.base.Objects;

import javax.management.remote.JMXServiceURL;

public class URLVirtualMachineDefinition extends VirtualMachineDefinition {

    private final JMXServiceURL url;

    public URLVirtualMachineDefinition(JMXServiceURL url) {
        this.url = url;
    }

    public JMXServiceURL getUrl() {
        return url;
    }

    @Override
    public String toString() {
        return Objects.toStringHelper(this)
                .add("url", url)
                .toString();
    }

    @Override
    public int hashCode() {
        return Objects.hashCode(url);
    }
}

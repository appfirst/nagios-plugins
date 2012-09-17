package com.objectstyle.appfirst.jmx.collector.management;

import com.google.common.collect.HashMultimap;
import com.google.common.collect.SetMultimap;
import com.objectstyle.appfirst.jmx.collector.command.VirtualMachineDefinition;
import com.objectstyle.appfirst.jmx.collector.resolve.*;

import javax.management.MBeanServerConnection;
import javax.management.remote.JMXServiceURL;
import java.io.IOException;

public class ManagementConnectionFactory implements VirtualMachineIdentifierInvalidationListener {
    private JMXConnectorPool connectorPool = new JMXConnectorPool();

    private VirtualMachineResolver resolver = new CachingLocalVirtualMachineResolver();

    private SetMultimap<JMXServiceURL, VirtualMachineIdentifier> availableIdentifiers = HashMultimap.create();

    public synchronized MBeanServerConnection getConnection(VirtualMachineDefinition definition)
            throws VirtualMachineResolverException, IOException {
        VirtualMachineIdentifier identifier = resolveIdentifier(definition);
        return getConnection(identifier);
    }

    private VirtualMachineIdentifier resolveIdentifier(VirtualMachineDefinition definition)
            throws VirtualMachineResolverException {
        VirtualMachineIdentifier identifier = resolver.resolve(definition);
        availableIdentifiers.put(identifier.getUrl(), identifier);
        identifier.addInvalidationListener(this);
        return identifier;
    }

    private MBeanServerConnection getConnection(VirtualMachineIdentifier identifier) throws IOException {
        return connectorPool.get(identifier.getUrl()).getMBeanServerConnection();
    }

    @Override
    public synchronized void identifierInvalidated(VirtualMachineIdentifier identifier) {
        availableIdentifiers.remove(identifier.getUrl(), identifier);
        if (availableIdentifiers.get(identifier.getUrl()).isEmpty()) {
            connectorPool.remove(identifier.getUrl());
        }
    }

    public void closeConnection(VirtualMachineDefinition definition) {
        try {
            resolveIdentifier(definition).invalidate();
        } catch (VirtualMachineResolverException e) {
            // if virtual machine could not been found then connection for it might had already been closed
        }
    }
}

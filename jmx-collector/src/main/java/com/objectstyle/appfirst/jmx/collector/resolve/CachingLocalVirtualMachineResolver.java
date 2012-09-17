package com.objectstyle.appfirst.jmx.collector.resolve;

import com.objectstyle.appfirst.jmx.collector.command.PatternVirtualMachineDefinition;
import com.objectstyle.appfirst.jmx.collector.command.URLVirtualMachineDefinition;
import com.objectstyle.appfirst.jmx.collector.command.VirtualMachineDefinition;
import com.sun.tools.attach.VirtualMachine;
import com.sun.tools.attach.VirtualMachineDescriptor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class CachingLocalVirtualMachineResolver
        implements VirtualMachineResolver, VirtualMachineIdentifierInvalidationListener {
    private static final Logger LOGGER = LoggerFactory.getLogger(CachingLocalVirtualMachineResolver.class);

    private Map<VirtualMachineDefinition, VirtualMachineIdentifier> cachedIdentifiers
            = new HashMap<VirtualMachineDefinition, VirtualMachineIdentifier>();

    private LocalVirtualMachineResolver localVirtualMachineResolver
            = new LocalVirtualMachineResolver(new JvmstatVirtualMachineMatcher());

    private URLVirtualMachineResolver urlVirtualMachineResolver = new URLVirtualMachineResolver();

    @Override
    public synchronized VirtualMachineIdentifier resolve(VirtualMachineDefinition definition)
            throws VirtualMachineResolverException {
        LOGGER.debug("Resolving descriptor for the virtual machine definition {}", definition);
        if (cachedIdentifiers.containsKey(definition)) {
            VirtualMachineIdentifier identifier = cachedIdentifiers.get(definition);
            LOGGER.debug("Found cached identifier {} for the virtual machine definition {}", identifier, definition);
            if (!(identifier instanceof LocalVirtualMachineIdentifier)) {
                return identifier;
            } else {

                if (checkVirtualMachineExists(((LocalVirtualMachineIdentifier) identifier).getDescriptor())) {
                    LOGGER.debug("Virtual machine with identifier {} still exists. Returning it.", identifier);
                    return identifier;
                } else {
                    LOGGER.debug("Virtual machine with identifier {} does not exist. Invalidating identifier.", identifier);
                    identifier.invalidate();
                }
            }
        }

        VirtualMachineIdentifier identifier;
        if (definition instanceof PatternVirtualMachineDefinition) {
            LOGGER.debug("Delegating resolve for the definition {} to the local resolver", definition);
            identifier = localVirtualMachineResolver.resolve(definition);
        } else if (definition instanceof URLVirtualMachineDefinition) {
            LOGGER.debug("Delegating resolve for the definition {} to the URL resolver", definition);
            identifier = urlVirtualMachineResolver.resolve(definition);
        } else {
            throw new IllegalArgumentException("Unknown definition type");
        }
        cachedIdentifiers.put(definition, identifier);
        return identifier;
    }

    @SuppressWarnings("SuspiciousMethodCalls")
    @Override
    public void identifierInvalidated(VirtualMachineIdentifier identifier) {
        cachedIdentifiers.remove(identifier);
    }

    private boolean checkVirtualMachineExists(VirtualMachineDescriptor descriptor) {
        List<VirtualMachineDescriptor> availableDescriptors = VirtualMachine.list();
        return availableDescriptors.contains(descriptor);
    }
}

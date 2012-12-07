package com.objectstyle.appfirst.jmx.collector.resolve;

import com.google.common.base.Optional;
import com.google.common.base.Predicate;
import com.google.common.collect.Iterators;
import com.objectstyle.appfirst.jmx.collector.Application;
import com.objectstyle.appfirst.jmx.collector.command.PatternVirtualMachineDefinition;
import com.objectstyle.appfirst.jmx.collector.command.VirtualMachineDefinition;
import com.objectstyle.appfirst.jmx.collector.utils.JVMAttach;
import com.sun.tools.attach.AgentInitializationException;
import com.sun.tools.attach.AgentLoadException;
import com.sun.tools.attach.AttachNotSupportedException;
import com.sun.tools.attach.VirtualMachine;
import com.sun.tools.attach.VirtualMachineDescriptor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import sun.tools.jconsole.LocalVirtualMachine;

import javax.management.remote.JMXServiceURL;
import java.io.File;
import java.io.IOException;
import java.net.MalformedURLException;
import java.util.Iterator;
import java.util.List;
import java.util.Properties;

public class LocalVirtualMachineResolver implements VirtualMachineResolver {
    public static final Logger LOGGER = LoggerFactory.getLogger(LocalVirtualMachineResolver.class);

    private static final String CONNECTOR_ADDRESS_PROPERTY = "com.sun.management.jmxremote.localConnectorAddress";

    private final VirtualMachineMatcher matcher;

    public LocalVirtualMachineResolver(VirtualMachineMatcher matcher) {
        this.matcher = matcher;
    }

    private class MatchDelegationPredicate implements Predicate<VirtualMachineDescriptor> {
        private final VirtualMachineDefinition definition;

        public MatchDelegationPredicate(VirtualMachineDefinition definition) {
            this.definition = definition;
        }

        @Override
        public boolean apply(VirtualMachineDescriptor input) {
            LOGGER.trace("Matching descriptor {} with definition {}", input, definition);
            return matcher.matches(definition, input);
        }
    }

    @Override
    public VirtualMachineIdentifier resolve(final VirtualMachineDefinition definition)
            throws VirtualMachineResolverException {
        if (!(definition instanceof PatternVirtualMachineDefinition)) {
            throw new IllegalArgumentException("Locale resolver supports pattern definitions only");
        }
        LOGGER.debug("Resolving descriptor for the virtual machine definition {}", definition);
        VirtualMachineDescriptor descriptor = resolveVirtualMachineDescriptor(definition);
        LOGGER.debug("Found descriptor for the virtual machine definition {}: {}", definition, descriptor);
        try {
            LOGGER.debug("Attaching to the virtual machine with descriptor {}", descriptor);
			JMXServiceURL url = isTestMode() ? attachForTestMode(descriptor) : attach(descriptor);
			return new LocalVirtualMachineIdentifier(descriptor, url);

		} catch (Exception e) {
            throw new VirtualMachineResolverException("Unable to attach to the virtual machine", e);
        }
    }

    private boolean isTestMode() {
        return Boolean.valueOf(System.getProperty(Application.TEST_MODE));
    }

    private JMXServiceURL attach(VirtualMachineDescriptor descriptor) throws MalformedURLException, VirtualMachineResolverException {
		LocalVirtualMachine lvm = LocalVirtualMachine.getLocalVirtualMachine(Integer.valueOf(descriptor.id()));
		if (!lvm.isAttachable())
			throw new VirtualMachineResolverException(String.format("Unable to attach to the virtual machine pid: %s",descriptor.id()));
		if (!lvm.isManageable()){
			JVMAttach attach = new JVMAttach();
			attach.setLvm(lvm);
			lvm = attach.attach();
			if (lvm == null || !lvm.isManageable())
				throw new VirtualMachineResolverException(String.format("Unable to attach to the virtual machine pid: %s",descriptor.id()));
		}
		return new JMXServiceURL(lvm.connectorAddress());
	}

    private JMXServiceURL attachForTestMode(VirtualMachineDescriptor descriptor) throws IOException, AttachNotSupportedException, AgentInitializationException, AgentLoadException {
        LOGGER.debug("Attention: TEST mode attaching works...");
        VirtualMachine virtualMachine = VirtualMachine.attach(descriptor);
        return new JMXServiceURL(getVirtualMachineAddress(virtualMachine));
    }

	private VirtualMachineDescriptor resolveVirtualMachineDescriptor(VirtualMachineDefinition definition)
            throws VirtualMachineResolverException {
        List<VirtualMachineDescriptor> availableDescriptors = VirtualMachine.list();
        LOGGER.debug("Available virtual machine descriptors: {}", availableDescriptors);
        Iterator<VirtualMachineDescriptor> descriptorIterator = availableDescriptors.iterator();
        Optional<VirtualMachineDescriptor> descriptor
                = Iterators.tryFind(descriptorIterator, new MatchDelegationPredicate(definition));
        if (!descriptor.isPresent()) {
            throw new VirtualMachineNotFoundException(definition);
        }
        Optional<VirtualMachineDescriptor> anotherDescriptor
                = Iterators.tryFind(descriptorIterator, new MatchDelegationPredicate(definition));
        if (anotherDescriptor.isPresent()) {
            throw new NotUniqueVirtualMachineException(definition);
        }
        return descriptor.get();
    }

    private String getVirtualMachineAddress(VirtualMachine virtualMachine)
            throws IOException, AgentLoadException, AgentInitializationException {
        LOGGER.debug("Getting URL for the virtual machine with id {}", virtualMachine.id());
        Properties props = virtualMachine.getAgentProperties();
        String connectorAddress = props.getProperty(CONNECTOR_ADDRESS_PROPERTY);
        if (connectorAddress == null) {
            LOGGER.debug("Management agent for the virtual machine with id {} has not been loaded yet. Loading agent.",
                    virtualMachine.id());
            props = virtualMachine.getSystemProperties();
            String home = props.getProperty("java.home");
            String agent = home + File.separator + "lib" + File.separator + "management-agent.jar";
            virtualMachine.loadAgent(agent);
            props = virtualMachine.getAgentProperties();
            connectorAddress = props.getProperty(CONNECTOR_ADDRESS_PROPERTY);
        }
        LOGGER.debug("Got URL for the virtual machine with id {}: {}|", virtualMachine.id(), connectorAddress);
        return connectorAddress;
    }
}

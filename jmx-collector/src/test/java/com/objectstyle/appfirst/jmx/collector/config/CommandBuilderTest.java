package com.objectstyle.appfirst.jmx.collector.config;

import com.objectstyle.appfirst.jmx.collector.command.Command;
import com.objectstyle.appfirst.jmx.collector.command.CompositeValueDefinition;
import com.objectstyle.appfirst.jmx.collector.command.PatternVirtualMachineDefinition;
import com.objectstyle.appfirst.jmx.collector.command.ValueDefinition;
import org.junit.Rule;
import org.junit.Test;
import org.junit.rules.ExpectedException;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

public class CommandBuilderTest {
    @Rule
    public ExpectedException thrown = ExpectedException.none();

    @Test
    public void testBuildCommandWithSimpleValueDefinition() throws Exception {
        CommandBuilder commandBuilder = new CommandBuilder();
        commandBuilder.startCommand("Application.Runtime.Name");
        commandBuilder.startVirtualMachineMatchPattern("com.objectstyle.Application");
        commandBuilder.startMBeanName("java.lang:type=Runtime");
        commandBuilder.startMBeanAttribute("name");
        commandBuilder.endCommand();
        Command command = commandBuilder.buildCommand();

        assertEquals("Application.Runtime.Name", command.getName());
        assertTrue(command.getVirtualMachineDefinition() instanceof PatternVirtualMachineDefinition);
        assertEquals("com.objectstyle.Application",
                ((PatternVirtualMachineDefinition) command.getVirtualMachineDefinition()).getMatchPattern());
        assertEquals(ValueDefinition.class, command.getValueDefinition().getClass());
        assertEquals("java.lang:type=Runtime", command.getValueDefinition().getName());
        assertEquals("name", command.getValueDefinition().getAttribute());
    }

    @Test
    public void testBuildCommandWithCompositeValueDefinition() throws Exception {
        CommandBuilder commandBuilder = new CommandBuilder();
        commandBuilder.startCommand("Application.Memory.HeapMemoryUsage.Used");
        commandBuilder.startVirtualMachineMatchPattern("com.objectstyle.Application");
        commandBuilder.startMBeanName("java.lang:type=Memory");
        commandBuilder.startMBeanAttribute("heapMemoryUsage");
        commandBuilder.startMBeanAttributeKey("used");
        commandBuilder.endCommand();
        Command command = commandBuilder.buildCommand();

        assertEquals("Application.Memory.HeapMemoryUsage.Used", command.getName());
        assertTrue(command.getVirtualMachineDefinition() instanceof PatternVirtualMachineDefinition);
        assertEquals("com.objectstyle.Application",
                ((PatternVirtualMachineDefinition) command.getVirtualMachineDefinition()).getMatchPattern());
        assertEquals(CompositeValueDefinition.class, command.getValueDefinition().getClass());
        assertEquals("java.lang:type=Memory", command.getValueDefinition().getName());
        assertEquals("heapMemoryUsage", command.getValueDefinition().getAttribute());
        assertEquals("used", ((CompositeValueDefinition) command.getValueDefinition()).getAttributeKey());
    }

    @Test
    public void testThrowExceptionOnNotBuiltCommand() throws Exception {
        CommandBuilder builder = new CommandBuilder();

        thrown.expect(IllegalStateException.class);
        thrown.expectMessage("Command has not been built yet");

        builder.startCommand("test");
        builder.buildCommand();
    }
}

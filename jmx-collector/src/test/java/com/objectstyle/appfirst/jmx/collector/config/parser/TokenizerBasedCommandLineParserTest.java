package com.objectstyle.appfirst.jmx.collector.config.parser;

import com.objectstyle.appfirst.jmx.collector.config.CommandLineParserException;
import com.objectstyle.appfirst.jmx.collector.config.CommandLineProcessor;
import com.objectstyle.appfirst.jmx.collector.config.parser.TokenizerBasedCommandLineParser;
import org.jmock.Expectations;
import org.jmock.Mockery;
import org.jmock.Sequence;
import org.jmock.auto.Auto;
import org.jmock.auto.Mock;
import org.jmock.integration.junit4.JMock;
import org.jmock.integration.junit4.JUnit4Mockery;
import org.junit.Rule;
import org.junit.Test;
import org.junit.rules.ExpectedException;
import org.junit.runner.RunWith;

@RunWith(JMock.class)
public class TokenizerBasedCommandLineParserTest {
    private Mockery context = new JUnit4Mockery();

    @Rule
    public ExpectedException thrown = ExpectedException.none();

    @Mock
    private CommandLineProcessor processorMock;

    @Auto
    private Sequence processorSequence;

    @Test
    public void testThrowExceptionOnEmptyString() throws Exception {
        TokenizerBasedCommandLineParser parser = new TokenizerBasedCommandLineParser(processorMock);

        thrown.expect(CommandLineParserException.class);
        thrown.expectMessage("Unexpected end of command");

        parser.parse("");
    }

    @Test
    public void testThrowExceptionOnWrongCommandStart() throws Exception {
        TokenizerBasedCommandLineParser parser = new TokenizerBasedCommandLineParser(processorMock);

        thrown.expect(CommandLineParserException.class);
        thrown.expectMessage("Unknown command keyword");

        parser.parse("wrong_command");
    }

    @Test
    public void testThrowExceptionOnWrongCommandNameStart() throws Exception {
        TokenizerBasedCommandLineParser parser = new TokenizerBasedCommandLineParser(processorMock);

        thrown.expect(CommandLineParserException.class);
        thrown.expectMessage("'[' is expected after jmx_command");

        parser.parse("jmx_command;Application.Runtime.Name");
    }

    @Test
    public void testThrowExceptionOnWrongCommandNameEnd() throws Exception {
        TokenizerBasedCommandLineParser parser = new TokenizerBasedCommandLineParser(processorMock);

        thrown.expect(CommandLineParserException.class);
        thrown.expectMessage("']' is expected after command name");

        parser.parse("jmx_command[Application.Runtime.Name;");
    }

    @Test
    public void testParseCommandName() throws Exception {
        TokenizerBasedCommandLineParser parser = new TokenizerBasedCommandLineParser(processorMock);

        context.checking(new Expectations() {
            {
                oneOf(processorMock).startCommand("Application.Runtime.Name");
                inSequence(processorSequence);

                oneOf(processorMock).endCommand();
                inSequence(processorSequence);
            }
        });

        parser.parse("jmx_command[Application.Runtime.Name]");
    }

    @Test
    public void testParseEmptyCommandName() throws Exception {
        TokenizerBasedCommandLineParser parser = new TokenizerBasedCommandLineParser(processorMock);

        context.checking(new Expectations() {
            {
                oneOf(processorMock).startCommand("");
                inSequence(processorSequence);

                oneOf(processorMock).endCommand();
                inSequence(processorSequence);
            }
        });

        parser.parse("jmx_command[]");
    }

    @Test
    public void testThrowExceptionWhenExpectingAttributeKey() throws Exception {
        TokenizerBasedCommandLineParser parser = new TokenizerBasedCommandLineParser(processorMock);

        context.checking(new Expectations() {
            {
                oneOf(processorMock).startCommand("Application.Runtime.Name");
            }
        });

        thrown.expect(CommandLineParserException.class);
        thrown.expectMessage("Attribute key is expected but got \"java.lang:type=Runtime\"");

        parser.parse("jmx_command[Application.Runtime.Name] java.lang:type=Runtime");
    }

    @Test
    public void testThrowExceptionWhenExpectingAttributeValue() throws Exception {
        TokenizerBasedCommandLineParser parser = new TokenizerBasedCommandLineParser(processorMock);

        context.checking(new Expectations() {
            {
                oneOf(processorMock).startCommand("Application.Runtime.Name");
            }
        });

        thrown.expect(CommandLineParserException.class);
        thrown.expectMessage("Attribute value expected but no more tokens left");

        parser.parse("jmx_command[Application.Runtime.Name] -P");
    }

    @Test
    public void testThrowExceptionOnUnknownAttributeKey() throws Exception {
        TokenizerBasedCommandLineParser parser = new TokenizerBasedCommandLineParser(processorMock);

        context.checking(new Expectations() {
            {
                oneOf(processorMock).startCommand("Application.Runtime.Name");
            }
        });

        thrown.expect(CommandLineParserException.class);
        thrown.expectMessage("Unknown attribute key \"-X\"");

        parser.parse("jmx_command[Application.Runtime.Name] -X value");
    }

    @Test
    public void testParseVirtualMachineMatchPattern() throws Exception {
        TokenizerBasedCommandLineParser parser = new TokenizerBasedCommandLineParser(processorMock);

        context.checking(new Expectations() {
            {
                oneOf(processorMock).startCommand("Application.Runtime.Name");
                inSequence(processorSequence);

                oneOf(processorMock).startVirtualMachineMatchPattern("com.objectstyle.Application");
                inSequence(processorSequence);

                oneOf(processorMock).endCommand();
                inSequence(processorSequence);
            }
        });

        parser.parse("jmx_command[Application.Runtime.Name] -P com.objectstyle.Application");
    }

    @Test
    public void testParseMBeanName() throws Exception {
        TokenizerBasedCommandLineParser parser = new TokenizerBasedCommandLineParser(processorMock);

        context.checking(new Expectations() {
            {
                oneOf(processorMock).startCommand("Application.Runtime.Name");
                inSequence(processorSequence);

                oneOf(processorMock).startMBeanName("java.lang:type=Runtime");
                inSequence(processorSequence);

                oneOf(processorMock).endCommand();
                inSequence(processorSequence);
            }
        });

        parser.parse("jmx_command[Application.Runtime.Name] -O java.lang:type=Runtime");
    }

    @Test
    public void testParseMBeanAttribute() throws Exception {
        TokenizerBasedCommandLineParser parser = new TokenizerBasedCommandLineParser(processorMock);

        context.checking(new Expectations() {
            {
                oneOf(processorMock).startCommand("Application.Runtime.Name");
                inSequence(processorSequence);

                oneOf(processorMock).startMBeanAttribute("name");
                inSequence(processorSequence);

                oneOf(processorMock).endCommand();
                inSequence(processorSequence);
            }
        });

        parser.parse("jmx_command[Application.Runtime.Name] -A name");
    }

    @Test
    public void testParseMBeanAttributeKey() throws Exception {
        TokenizerBasedCommandLineParser parser = new TokenizerBasedCommandLineParser(processorMock);

        context.checking(new Expectations() {
            {
                oneOf(processorMock).startCommand("Application.Memory.HeapMemoryUsage.Used");
                inSequence(processorSequence);

                oneOf(processorMock).startMBeanAttributeKey("used");
                inSequence(processorSequence);

                oneOf(processorMock).endCommand();
                inSequence(processorSequence);
            }
        });

        parser.parse("jmx_command[Application.Memory.HeapMemoryUsage.Used] -K used");
    }

    @Test
    public void testFullParseVariant1() throws Exception {
        TokenizerBasedCommandLineParser parser = new TokenizerBasedCommandLineParser(processorMock);

        context.checking(new Expectations() {
            {
                oneOf(processorMock).startCommand("Application.Runtime.Name");
                inSequence(processorSequence);

                oneOf(processorMock).startVirtualMachineMatchPattern("com.objectstyle.Application");
                inSequence(processorSequence);

                oneOf(processorMock).startMBeanName("java.lang:type=Runtime");
                inSequence(processorSequence);

                oneOf(processorMock).startMBeanAttribute("name");
                inSequence(processorSequence);

                oneOf(processorMock).endCommand();
                inSequence(processorSequence);
            }
        });

        parser.parse("jmx_command[Application.Runtime.Name] -P com.objectstyle.Application -O java.lang:type=Runtime -A name");
    }

    @Test
    public void testFullParseVariant2() throws Exception {
        TokenizerBasedCommandLineParser parser = new TokenizerBasedCommandLineParser(processorMock);

        context.checking(new Expectations() {
            {
                oneOf(processorMock).startCommand("Application.Memory.HeapMemoryUsage.Used");
                inSequence(processorSequence);

                oneOf(processorMock).startVirtualMachineMatchPattern("com.objectstyle.Application");
                inSequence(processorSequence);

                oneOf(processorMock).startMBeanName("java.lang:type=Memory");
                inSequence(processorSequence);

                oneOf(processorMock).startMBeanAttribute("heapMemoryUsage");
                inSequence(processorSequence);

                oneOf(processorMock).startMBeanAttributeKey("used");
                inSequence(processorSequence);

                oneOf(processorMock).endCommand();
                inSequence(processorSequence);
            }
        });

        parser.parse("jmx_command[Application.Memory.HeapMemoryUsage.Used] -P com.objectstyle.Application -O java.lang:type=Memory -A heapMemoryUsage -K used");
    }
}

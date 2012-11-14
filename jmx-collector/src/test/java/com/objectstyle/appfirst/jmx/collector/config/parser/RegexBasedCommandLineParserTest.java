package com.objectstyle.appfirst.jmx.collector.config.parser;

import com.objectstyle.appfirst.jmx.collector.config.CommandLineProcessor;
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
public class RegexBasedCommandLineParserTest {
    private Mockery context = new JUnit4Mockery();

    @Rule
    public ExpectedException thrown = ExpectedException.none();

    @Mock
    private CommandLineProcessor processorMock;

    @Auto
    private Sequence processorSequence;

    @Test
    public void testFullParseVariant1() throws Exception {

    RegexBasedCommandLineParser parser = new RegexBasedCommandLineParser(processorMock);

        context.checking(new Expectations() {
            {
                oneOf(processorMock).startCommand("nycstgpjbsapp01-as1-NonHeapMemoryUsage");
                inSequence(processorSequence);

                oneOf(processorMock).startMBeanName("java.lang:type=Memory");
                inSequence(processorSequence);

                oneOf(processorMock).startMBeanAttribute("NonHeapMemoryUsage");
                inSequence(processorSequence);

                oneOf(processorMock).startVirtualMachineMatchPattern("as1");
                inSequence(processorSequence);

                oneOf(processorMock).startMBeanAttributeKey("used");
                inSequence(processorSequence);

                oneOf(processorMock).endCommand();
                inSequence(processorSequence);
            }
        });
        parser.parse("jmx_command[nycstgpjbsapp01-as1-NonHeapMemoryUsage] -P as1 -O java.lang:type=Memory -A NonHeapMemoryUsage -K used");
    }

    @Test
    public void testFullParseVariant2() throws Exception {

    RegexBasedCommandLineParser parser = new RegexBasedCommandLineParser(processorMock);

        context.checking(new Expectations() {
            {
                oneOf(processorMock).startCommand("nycstgpjbsapp01-as1-ThreadPool");
                inSequence(processorSequence);

                oneOf(processorMock).startMBeanName("jboss.web:type=ThreadPool,name=ajp-nycstgpjbsapp01-as1 172.16.78.152-8009");
                inSequence(processorSequence);

                oneOf(processorMock).startMBeanAttribute("currentThreadsBusy");
                inSequence(processorSequence);

                oneOf(processorMock).startVirtualMachineMatchPattern("as1");
                inSequence(processorSequence);

                oneOf(processorMock).endCommand();
                inSequence(processorSequence);
            }
        });
        parser.parse("jmx_command[nycstgpjbsapp01-as1-ThreadPool] -P as1 -O jboss.web:type=ThreadPool,name=ajp-nycstgpjbsapp01-as1 172.16.78.152-8009 -A currentThreadsBusy");
    }
}

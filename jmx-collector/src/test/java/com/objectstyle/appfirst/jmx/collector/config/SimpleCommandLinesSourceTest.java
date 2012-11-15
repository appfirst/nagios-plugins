package com.objectstyle.appfirst.jmx.collector.config;

import com.google.common.io.InputSupplier;
import org.jmock.Expectations;
import org.jmock.Mockery;
import org.jmock.api.Invocation;
import org.jmock.auto.Mock;
import org.jmock.integration.junit4.JMock;
import org.jmock.integration.junit4.JUnit4Mockery;
import org.jmock.lib.action.CustomAction;
import org.junit.Test;
import org.junit.runner.RunWith;

import java.io.IOException;
import java.nio.CharBuffer;
import java.util.List;

import static junit.framework.Assert.assertEquals;
import static junit.framework.Assert.assertTrue;
import static junit.framework.Assert.assertFalse;

@RunWith(JMock.class)
public class SimpleCommandLinesSourceTest {
    private static final String TEST_CONFIG_DATA = "command[check_load]=/usr/share/appfirst/plugins/libexec/check_load -w 15,10,5 -c 30,25,20\n"
            + "jmx_command[Application.Runtime.Name] -P com.objectstyle.Application -O java.lang:type=Runtime -A name\u2028\u2028\n"
            + "jmx_command[Application.Memory.HeapMemoryUsage.Used] -P com.objectstyle.Application -O java.lang:type=Memory -A heapMemoryUsage -K used";

    private Mockery context = new JUnit4Mockery();

    @Mock
    private Readable readableMock;

    private class ReadableMockInputSupplier implements InputSupplier<Readable> {
        @Override
        public Readable getInput() throws IOException {
            return readableMock;
        }
    }

    @Test
    public void testReadCommandStrings() throws Exception {
        SimpleCommandLinesSource source = new SimpleCommandLinesSource(new ReadableMockInputSupplier());

        context.checking(new Expectations() {
            {
                oneOf(readableMock).read(with(aNonNull(CharBuffer.class)));
                will(new CustomAction("provide with configuration") {
                    @Override
                    public Object invoke(Invocation invocation) throws Throwable {
                        CharBuffer buffer = (CharBuffer) invocation.getParameter(0);
                        buffer.append(TEST_CONFIG_DATA);
                        return TEST_CONFIG_DATA.length();
                    }
                });

                allowing(readableMock).read(with(aNonNull(CharBuffer.class)));
                will(returnValue(-1));
            }
        });

        List<String> commandStrings = source.readLines();
        assertEquals(2, commandStrings.size());
        for (String string : commandStrings) {
            assertTrue(string.startsWith("jmx_command"));
            assertFalse(Character.isWhitespace(string.toCharArray()[string.length()-1]));
        }
    }
}

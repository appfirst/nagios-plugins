package com.objectstyle.appfirst.jmx.collector.output;

import com.objectstyle.appfirst.jmx.collector.output.af.AfCollector;
import com.objectstyle.appfirst.jmx.collector.result.Result;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import static com.objectstyle.appfirst.jmx.collector.output.af.AfCollector.AFCollectorReturnCode;
import static com.objectstyle.appfirst.jmx.collector.output.af.AfCollector.postAFCollectorMessage;

public class AfCollectorOutput extends QueuedOutput implements Output {
    private static final Logger LOGGER = LoggerFactory.getLogger(AfCollectorOutput.class);

    @Override
    protected void doWrite(Result result) {
        // This is our declared format
        /*String fullString = String.format("jmx_command[%s];status=%d;message=\"%s\"",
                result.getName(), result.getStatus().getNagiosIntValue(), result.toString());*/

        // This is format that proposed Pat
        String fullString = String.format("%s:%s:%d", result.getName(),
                result.toString(), result.getStatus().getNagiosIntValue());

        LOGGER.debug("Posting message to the AppFirst collector: {}", fullString);
        AFCollectorReturnCode returnCode
                = postAFCollectorMessage(AfCollector.AFCollectorMsgSeverity.AFCSeverityPolled, fullString);
        LOGGER.debug("Returned code from the AppFirst collector: {}", returnCode);

        while (returnCode == AFCollectorReturnCode.AFCWouldBlock) {
            try {
                Thread.sleep(1000);
            } catch (InterruptedException e) {
                // ignoring
            }
            LOGGER.debug("Trying to post message to the AppFirst collector again: {}", fullString);
            returnCode = postAFCollectorMessage(AfCollector.AFCollectorMsgSeverity.AFCSeverityPolled, fullString);
        }
    }
}

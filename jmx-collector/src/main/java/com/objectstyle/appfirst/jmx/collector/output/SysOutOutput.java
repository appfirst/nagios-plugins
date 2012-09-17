package com.objectstyle.appfirst.jmx.collector.output;

import com.objectstyle.appfirst.jmx.collector.result.Result;

public class SysOutOutput extends QueuedOutput implements Output {
    @Override
    public void doWrite(Result result) {
        System.out.println(result.toString());
    }
}

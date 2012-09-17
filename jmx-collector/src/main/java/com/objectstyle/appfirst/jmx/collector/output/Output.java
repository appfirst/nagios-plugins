package com.objectstyle.appfirst.jmx.collector.output;

import com.objectstyle.appfirst.jmx.collector.result.Result;

public interface Output {
    void write(Result result);
}

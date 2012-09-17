package com.objectstyle.appfirst.jmx.collector.execution;

import com.objectstyle.appfirst.jmx.collector.command.Command;
import com.objectstyle.appfirst.jmx.collector.result.Result;

public interface CommandExecutor {
    Result execute(Command command) throws CommandExecutionException;
}

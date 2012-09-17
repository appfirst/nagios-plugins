package com.objectstyle.appfirst.jmx.collector.execution;

import com.google.common.util.concurrent.*;
import com.objectstyle.appfirst.jmx.collector.command.Command;
import com.objectstyle.appfirst.jmx.collector.management.ManagementConnectionFactory;
import com.objectstyle.appfirst.jmx.collector.output.Output;
import com.objectstyle.appfirst.jmx.collector.result.Result;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.concurrent.Callable;
import java.util.concurrent.ConcurrentMap;
import java.util.concurrent.Executors;

public class CommandsExecutionLifecycle implements Runnable {
    private static final Logger LOGGER = LoggerFactory.getLogger(CommandsExecutionLifecycle.class);

    private static final int DEFAULT_THREAD_POOL_SIZE = 4;

    private final ConcurrentMap<String, Command> commands;

    private final Output output;

    private final ListeningExecutorService executorService;

    private final ManagementConnectionFactory managementConnectionFactory;

    private final FutureCallback<Result> commandExecutionCallback = new FutureCallback<Result>() {
        @Override
        public void onSuccess(Result result) {
            onCommandExecutionSuccess(result);
        }

        @Override
        public void onFailure(Throwable t) {
            onCommandExecutionFailure(t);
        }
    };

    public CommandsExecutionLifecycle(ManagementConnectionFactory managementConnectionFactory,
                                      ConcurrentMap<String, Command> commands, Output output) {
        this.managementConnectionFactory = managementConnectionFactory;
        this.commands = commands;
        this.output = output;
        executorService = MoreExecutors.listeningDecorator(Executors.newFixedThreadPool(DEFAULT_THREAD_POOL_SIZE));
    }

    @Override
    public void run() {
        LOGGER.debug("Starting new command execution cycle");
        LOGGER.debug("There are {} command to execute", commands.size());
        for (final Command command : commands.values()) {
            LOGGER.debug("Submitting command for execution: {}", command.toString());
            ListenableFuture<Result> future = executorService.submit(new Callable<Result>() {
                @Override
                public Result call() throws Exception {
                    return new DefaultCommandExecutor(managementConnectionFactory).execute(command);
                }
            });
            Futures.addCallback(future, commandExecutionCallback);
        }
    }

    private void onCommandExecutionSuccess(Result result) {
        LOGGER.debug("Got execution result: {}", result.toString());
        output.write(result);
    }

    private void onCommandExecutionFailure(Throwable t) {
        LOGGER.error("Error occurred while executing command", t);
    }
}

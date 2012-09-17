package com.objectstyle.appfirst.jmx.collector.execution;

import com.google.common.collect.Maps;
import com.objectstyle.appfirst.jmx.collector.command.Command;
import com.objectstyle.appfirst.jmx.collector.config.*;
import com.objectstyle.appfirst.jmx.collector.management.ManagementConnectionFactory;
import com.objectstyle.appfirst.jmx.collector.output.Output;
import com.objectstyle.appfirst.jmx.collector.result.ParseErrorResult;
import com.objectstyle.appfirst.jmx.collector.result.ValidationErrorResult;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;

import static java.lang.String.format;

public class CommandsUpdateLifecycle implements Runnable {
    private static final Logger LOGGER = LoggerFactory.getLogger(CommandsUpdateLifecycle.class);

    private final CommandLinesSource commandLinesSource;

    private final Output output;

    private final ConcurrentMap<String, Command> commands;

    private final ManagementConnectionFactory managementConnectionFactory;

    public CommandsUpdateLifecycle(ManagementConnectionFactory managementConnectionFactory,
                                   CommandLinesSource commandLinesSource, Output output) {
        this.managementConnectionFactory = managementConnectionFactory;
        this.commandLinesSource = commandLinesSource;
        this.output = output;
        commands = new ConcurrentHashMap<String, Command>();
    }

    public ConcurrentMap<String, Command> getCommands() {
        return commands;
    }

    @Override
    public void run() {
        LOGGER.debug("Starting new commands update cycle");
        Map<String, Command> updatedCommands = new HashMap<String, Command>();
        if (getUpdates(updatedCommands)) {
            mergeCommands(updatedCommands);
        }
    }

    private boolean getUpdates(Map<String, Command> updatedCommands) {
        try {
            if (!commandLinesSource.hasChanges()) {
                LOGGER.debug("There are no changes in the source. Nothing to update.");
            } else {
                LOGGER.debug("There are changes in the source. Updating commands.");
                List<String> commandLines = commandLinesSource.readLines();
                LOGGER.debug("Got {} line/lines from the source. Now parsing them.", commandLines.size());
                CommandBuilder builder = new CommandBuilder();
                CommandLineParser parser = new CommandLineParser(builder);
                for (String line : commandLines) {
                    try {
                        parser.parse(line);
                        Command command = builder.buildCommand();
                        updatedCommands.put(command.getName(), command);
                    } catch (CommandLineParserException e) {
                        LOGGER.warn("Command parse error", e);
                        output.write(new ParseErrorResult(e));
                    } catch (CommandValidationException e) {
                        LOGGER.warn("Command validation error", e);
                        output.write(new ValidationErrorResult(e));
                    }
                }
                return true;
            }
        } catch (IOException e) {
            LOGGER.error("Error while reading the configuration");
        }
        return false;
    }

    private void mergeCommands(Map<String, Command> updatedCommands) {
        LOGGER.debug("Merging commands");
        int added = 0, updated = 0, removed = 0;
        for (Command command : updatedCommands.values()) {
            if (commands.replace(command.getName(), command) != null) {
                updated++;
            }
            if (commands.putIfAbsent(command.getName(), command) == null) {
                added++;
            }
        }
        for (Command command : Maps.difference(commands, updatedCommands).entriesOnlyOnLeft().values()) {
            if (commands.remove(command.getName(), command)) {
                removed++;
                managementConnectionFactory.closeConnection(command.getVirtualMachineDefinition());
            }
        }
        if (LOGGER.isDebugEnabled()) {
            LOGGER.debug(format("There were %d new, %d updated and %d removed commands", added, updated, removed));
        }
    }
}

package com.objectstyle.appfirst.jmx.collector.config.parser;

import com.objectstyle.appfirst.jmx.collector.config.CommandLineParserException;
import com.objectstyle.appfirst.jmx.collector.config.CommandLineProcessor;
import com.objectstyle.appfirst.jmx.collector.config.Constants;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.HashMap;
import java.util.Map;
import java.util.StringTokenizer;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class RegexBasedCommandLineParser implements CommandLineParser {
    private static final Logger LOGGER = LoggerFactory.getLogger(RegexBasedCommandLineParser.class);
    private static final Pattern PATTERN = Pattern.compile("jmx_command\\[(.+)\\] -(\\w) (.[^-]+) -(O) (.+) -(A) (.[^-]+)(-(\\w) (.[^-]+))?(-(\\w) (.[^-]+))?(-(\\w) (.[^-]+))?"
    );
    private CommandLineProcessor processor;

    public RegexBasedCommandLineParser(CommandLineProcessor processor) {
        this.processor = processor;
    }

    @Override
    public void parse(String commandLine) throws CommandLineParserException {
        LOGGER.debug("Starting command string parse: {}", commandLine);
        StringTokenizer tokenizer = new StringTokenizer(commandLine, " \t");
        if (!tokenizer.hasMoreTokens()) {
            throw new CommandLineParserException("Unexpected end of command");
        }
        if (!commandLine.startsWith(Constants.COMMAND_KEYWORD)) {
            throw new CommandLineParserException("Unknown command keyword");
        }
        parseCommandAttributes(commandLine);
        processor.endCommand();
        LOGGER.debug("Command string successfully parsed");
    }

    protected void parseCommandAttributes(String commandLine) throws CommandLineParserException {
        LOGGER.trace("Parsing command attributes...");
        Matcher matcher = PATTERN.matcher(commandLine);
        if (matcher.matches()) {
            LOGGER.trace("Starting attribute parse...");

            String commandName = matcher.group(1);
            if (commandName != null && commandName.length() > 0) {
                LOGGER.trace("Found command name: {}", commandName);
                processor.startCommand(commandName);
            }
            else {
                throw new CommandLineParserException("Command name shouldn't be empty");
            }

            Map<String, String> options = new HashMap<String, String>(6);

            // 3 pair of groups are reserved for mandatory parameters (-P/-U, -O, -A)
            for (int i = 2; i < 7; i = i + 2) {
                handleParameterGroups(matcher, options, i);
            }

            // other 3 pair of groups are reserved for optional parameters (-K, -W, -C)
            for (int i = 9; matcher.group(i) != null; i = i + 3) {
                handleParameterGroups(matcher, options, i);
            }

            for (Map.Entry<String, String> entry : options.entrySet()) {
                processAttribute(entry);
            }
        }
    }

    private void handleParameterGroups(Matcher matcher, Map<String, String> options, int groupIndex) throws CommandLineParserException {
        String group1 = matcher.group(groupIndex);
        String group2 = matcher.group(groupIndex + 1);
        if (group1 != null && group2 !=null) {
            options.put(group1.trim(), group2.trim());
        }
        else {
            throw new CommandLineParserException("JMX Command is malformed.");
        }
    }

    private void processAttribute(Map.Entry<String, String> entry) throws CommandLineParserException {
        LOGGER.trace("[-"+entry.getKey() + " " + entry.getValue() + "] is being processed...");

        if (entry.getKey().equals("P")) {
            processor.startVirtualMachineMatchPattern(entry.getValue());
        }
        else if (entry.getKey().equals("U")) {
            processor.startVirtualMachineURL(entry.getValue());
        }
        else if (entry.getKey().equals("O")) {
            processor.startMBeanName(entry.getValue());
        }
        else if (entry.getKey().equals("A")) {
            processor.startMBeanAttribute(entry.getValue());
        }
        else if (entry.getKey().equals("K")) {
            processor.startMBeanAttributeKey(entry.getValue());
        }
        else if (entry.getKey().equals("W")) {
            processor.startWarningThreshold(entry.getValue());
        }
        else if (entry.getKey().equals("C")) {
            processor.startCriticalThreshold(entry.getValue());
        }
        else {
            throw new CommandLineParserException("Unknown attribute key \"" + entry.getKey() + "\"");
        }
    }
}

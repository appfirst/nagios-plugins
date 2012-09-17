package com.objectstyle.appfirst.jmx.collector.config;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.StringTokenizer;

public class CommandLineParser {
    private static final Logger LOGGER = LoggerFactory.getLogger(CommandLineParser.class);

    private final CommandLineProcessor processor;

    public CommandLineParser(CommandLineProcessor processor) {
        this.processor = processor;
    }

    public void parse(String commandLine) throws CommandLineParserException {
        LOGGER.debug("Starting command string parse: {}", commandLine);
        StringTokenizer tokenizer = new StringTokenizer(commandLine, " \t");
        if (!tokenizer.hasMoreTokens()) {
            throw new CommandLineParserException("Unexpected end of command");
        }
        parseCommandHead(tokenizer.nextToken());
        parseCommandAttributes(tokenizer);
        processor.endCommand();
        LOGGER.debug("Command string successfully parsed");
    }

    private void parseCommandHead(String commandHead) throws CommandLineParserException {
        LOGGER.trace("Parsing command head: {}", commandHead);
        if (!commandHead.startsWith(Constants.COMMAND_KEYWORD)) {
            throw new CommandLineParserException("Unknown command keyword");
        }
        if (commandHead.charAt(Constants.COMMAND_KEYWORD.length()) != '[') {
            throw new CommandLineParserException("'[' is expected after jmx_command");
        }
        if (commandHead.charAt(commandHead.length() - 1) != ']') {
            throw new CommandLineParserException("']' is expected after command name");
        }
        String commandName = commandHead.substring(Constants.COMMAND_KEYWORD.length() + 1, commandHead.length() - 1);
        LOGGER.trace("Found command name: {}", commandName);
        processor.startCommand(commandName);
    }

    private void parseCommandAttributes(StringTokenizer tokenizer) throws CommandLineParserException {
        LOGGER.trace("Parsing command attributes...");
        while (tokenizer.hasMoreTokens()) {
            LOGGER.trace("Starting attribute parse...");
            String attributeKey = tokenizer.nextToken();
            if (!attributeKey.startsWith(Constants.ATTRIBUTE_KEY_PREFIX)) {
                throw new CommandLineParserException("Attribute key is expected but got \"" + attributeKey + "\"");
            }
            LOGGER.trace("Found attribute key: {}", attributeKey);
            String attributeValue;
            if (tokenizer.hasMoreTokens()) {
                attributeValue = tokenizer.nextToken();
            } else {
                throw new CommandLineParserException("Attribute value expected but no more tokens left");
            }
            LOGGER.trace("Found attribute value: {}", attributeValue);
            processAttribute(attributeKey, attributeValue);
        }
    }

    private void processAttribute(String attributeKey, String attributeValue) throws CommandLineParserException {
        LOGGER.trace("Processing attribute...");
        if (attributeKey.equals(Constants.VIRTUAL_MACHINE_MATCH_PATTERN_KEY)) {
            processor.startVirtualMachineMatchPattern(attributeValue);
        } else if (attributeKey.equals(Constants.VIRTUAL_MACHINE_URL_KEY)) {
            processor.startVirtualMachineURL(attributeValue);
        } else if (attributeKey.equals(Constants.MBEAN_NAME_KEY)) {
            processor.startMBeanName(attributeValue);
        } else if (attributeKey.equals(Constants.MBEAN_ATTRIBUTE_KEY)) {
            processor.startMBeanAttribute(attributeValue);
        } else if (attributeKey.equals(Constants.MBEAN_ATTRIBUTE_KEY_KEY)) {
            processor.startMBeanAttributeKey(attributeValue);
        } else if (attributeKey.equals(Constants.WARNING_THRESHOLD_KEY)) {
            processor.startWarningThreshold(attributeValue);
        } else if (attributeKey.equals(Constants.CRITICAL_THRESHOLD_KEY)) {
            processor.startCriticalThreshold(attributeValue);
        } else {
            throw new CommandLineParserException("Unknown attribute key \"" + attributeKey + "\"");
        }
    }
}

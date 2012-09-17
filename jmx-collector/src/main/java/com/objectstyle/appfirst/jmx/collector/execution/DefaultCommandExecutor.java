package com.objectstyle.appfirst.jmx.collector.execution;

import com.google.common.base.Function;
import com.google.common.base.Optional;
import com.google.common.base.Predicate;
import com.google.common.collect.Iterators;
import com.google.common.primitives.Primitives;
import com.objectstyle.appfirst.jmx.collector.command.Command;
import com.objectstyle.appfirst.jmx.collector.command.CompositeValueDefinition;
import com.objectstyle.appfirst.jmx.collector.command.ValueDefinition;
import com.objectstyle.appfirst.jmx.collector.management.ManagementConnectionFactory;
import com.objectstyle.appfirst.jmx.collector.resolve.VirtualMachineResolverException;
import com.objectstyle.appfirst.jmx.collector.result.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import javax.management.*;
import javax.management.openmbean.OpenMBeanAttributeInfo;
import javax.management.openmbean.OpenType;
import java.io.IOException;
import java.util.HashSet;
import java.util.Set;

import static com.google.common.collect.Collections2.transform;

public class DefaultCommandExecutor implements CommandExecutor {
    private static final Logger LOGGER = LoggerFactory.getLogger(DefaultCommandExecutor.class);

    private final ManagementConnectionFactory managementConnectionFactory;

    private final ThresholdChecker thresholdChecker;

    public DefaultCommandExecutor(ManagementConnectionFactory managementConnectionFactory) {
        this.managementConnectionFactory = managementConnectionFactory;
        thresholdChecker = new DelegatingThresholdChecker();
    }

    @Override
    public Result execute(Command command) throws CommandExecutionException {
        LOGGER.debug("Starting command execution: {}", command);
        MBeanServerConnection connection;
        try {
            LOGGER.debug("Getting managing connection");
            connection = managementConnectionFactory.getConnection(command.getVirtualMachineDefinition());
        } catch (VirtualMachineResolverException e) {
            LOGGER.warn("Error while connecting to the virtual machine", e);
            return new ErrorResult(command.getName(), "Can't resolve the virtual machine");
        } catch (IOException e) {
            LOGGER.warn("Error while connecting to the virtual machine", e);
            return new ErrorResult(command.getName(), "Can't connect to the virtual machine");
        }
        ValueDefinition valueDefinition = command.getValueDefinition();
        LOGGER.debug("Reading value from MBean");
        ResultData resultData = readValueFromMBean(connection, valueDefinition);
        LOGGER.debug("Got result: {}", resultData);
        ResultStatus status;
        if (resultData instanceof ErrorResultData) {
            LOGGER.debug("There were errors in the command execution, setting status to EXECUTION_ERROR");
            status = ResultStatus.EXECUTION_ERROR;
        } else {
            LOGGER.debug("Handling thresholds");
            status = handleThresholds(command, resultData);
        }
        Result result = new Result(command.getName(), status, resultData);
        LOGGER.debug("Command execution finished. Returning result: {}", result);
        return result;
    }

    private ResultStatus handleThresholds(Command command, ResultData resultData) {
        if (thresholdChecker.checkReached(command.getCriticalThresholdDefinition(), resultData)) {
            LOGGER.debug("Reached critical threshold");
            return ResultStatus.CRITICAL_THRESHOLD;
        } else if (thresholdChecker.checkReached(command.getWarningThresholdDefinition(), resultData)) {
            LOGGER.debug("Reached warning threshold");
            return ResultStatus.WARNING_THRESHOLD;
        }
        return ResultStatus.REGULAR;
    }

    private ResultData readValueFromMBean(MBeanServerConnection connection, final ValueDefinition valueDefinition)
            throws CommandExecutionException {
        try {
            ObjectName objectName = new ObjectName(removeEscapeSymbols(valueDefinition.getName()));
            MBeanInfo info = connection.getMBeanInfo(objectName);
            Optional<MBeanAttributeInfo> attributeInfoOptional = Iterators.tryFind(Iterators.forArray(info.getAttributes()), new Predicate<MBeanAttributeInfo>() {
                @Override
                public boolean apply(MBeanAttributeInfo input) {
                    return input.getName().equals(valueDefinition.getAttribute());
                }
            });
            if (!attributeInfoOptional.isPresent()) {
                return new ErrorResultData("No such attribute");
            }
            Object value = connection.getAttribute(objectName, valueDefinition.getAttribute());
            ResultData data = convertData(attributeInfoOptional.get(), value);
            data = handleSingleKeyForCompositeData(valueDefinition, data);
            return data;
        } catch (MalformedObjectNameException e) {
            return new ErrorResultData("Malformed object name");
        } catch (UnsupportedDataTypeException e) {
            return new ErrorResultData(e.getLocalizedMessage());
        } catch (InstanceNotFoundException e) {
            return new ErrorResultData("Not such object");
        } catch (AttributeNotFoundException e) {
            throw new IllegalStateException("Attribute not found but attribute info exist for it", e);
        } catch (Exception e) {
            throw new CommandExecutionException(e);
        }
    }

    private static String removeEscapeSymbols(String string) {
        return string.replaceAll("\\\\", "");
    }

    private ResultData handleSingleKeyForCompositeData(ValueDefinition definition, ResultData data) {
        if (data instanceof CompositeResultData && definition instanceof CompositeValueDefinition) {
            CompositeResultData compositeData = (CompositeResultData) data;
            String key = ((CompositeValueDefinition) definition).getAttributeKey();
            if (compositeData.containsKey(key)) {
                return ((CompositeResultData) data).forSingleKey(key);
            } else {
                return new ErrorResultData("No such key for attribute with composite data");
            }
        }
        return data;
    }

    private ResultData convertData(MBeanAttributeInfo attributeInfo, Object value) throws UnsupportedDataTypeException {
        if (attributeInfo instanceof OpenMBeanAttributeInfo) {
            LOGGER.debug("Converting result from Open Type");
            return convertOpenMBeanData(((OpenMBeanAttributeInfo) attributeInfo).getOpenType(), value);
        } else if (isPrimitiveOrWrapperType(attributeInfo.getType())) {
            LOGGER.debug("Converting result from primitive: {}", attributeInfo.getType());
            return new SimpleResultData("val", value.toString());
        }
        throw new UnsupportedDataTypeException(attributeInfo.getType());
    }

    private boolean isPrimitiveOrWrapperType(String type) {
        Set<Class<?>> allTypes = new HashSet<Class<?>>();
        allTypes.addAll(Primitives.allPrimitiveTypes());
        allTypes.addAll(Primitives.allWrapperTypes());
        return transform(allTypes, new Function<Class<?>, String>() {
            @Override
            public String apply(Class<?> input) {
                return input.getName();
            }
        }).contains(type);
    }

    @SuppressWarnings("unchecked")
    private ResultData convertOpenMBeanData(OpenType<?> type, Object value) throws UnsupportedOpenTypeException {
        return OpenMBeanDataConverterFactory.INSTANCE.getConverter(type).convert(type, value);
    }

}

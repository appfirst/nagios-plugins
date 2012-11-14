package com.objectstyle.appfirst.jmx.collector.execution;

import com.objectstyle.appfirst.jmx.collector.command.Command;
import com.objectstyle.appfirst.jmx.collector.command.CompositeValueDefinition;
import com.objectstyle.appfirst.jmx.collector.command.ValueDefinition;
import com.objectstyle.appfirst.jmx.collector.management.ManagementConnectionFactory;
import com.objectstyle.appfirst.jmx.collector.resolve.VirtualMachineResolverException;
import com.objectstyle.appfirst.jmx.collector.result.CompositeResultData;
import com.objectstyle.appfirst.jmx.collector.result.ErrorResult;
import com.objectstyle.appfirst.jmx.collector.result.ErrorResultData;
import com.objectstyle.appfirst.jmx.collector.result.MBeanDataConverterFactory;
import com.objectstyle.appfirst.jmx.collector.result.OpenMBeanDataConverterFactory;
import com.objectstyle.appfirst.jmx.collector.result.Result;
import com.objectstyle.appfirst.jmx.collector.result.ResultData;
import com.objectstyle.appfirst.jmx.collector.result.ResultStatus;
import com.objectstyle.appfirst.jmx.collector.result.SimpleResultData;
import com.objectstyle.appfirst.jmx.collector.result.UnsupportedDataTypeException;
import org.apache.commons.collections.CollectionUtils;
import org.apache.commons.collections.Predicate;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import javax.management.AttributeNotFoundException;
import javax.management.InstanceNotFoundException;
import javax.management.MBeanAttributeInfo;
import javax.management.MBeanInfo;
import javax.management.MBeanServerConnection;
import javax.management.MalformedObjectNameException;
import javax.management.ObjectName;
import javax.management.openmbean.OpenMBeanAttributeInfo;
import javax.management.openmbean.OpenType;
import java.io.IOException;
import java.util.Arrays;

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
            MBeanAttributeInfo firstFoundAttributeInfo = (MBeanAttributeInfo) CollectionUtils.find(Arrays.asList(info.getAttributes()), new Predicate() {
                @Override
                public boolean evaluate(Object o) {
                    MBeanAttributeInfo attributeInfo = (MBeanAttributeInfo) o;
                    return attributeInfo.getName().equals(valueDefinition.getAttribute());
                }
            });

            if (firstFoundAttributeInfo == null) {
                return new ErrorResultData("No such attribute");
            }
            Object value = connection.getAttribute(objectName, valueDefinition.getAttribute());
            if (value !=null) {
                ResultData data = convertData(firstFoundAttributeInfo, value);
                return handleSingleKeyForCompositeData(valueDefinition, data);
            }
            else{
                return new SimpleResultData(null);
            }
        } catch (MalformedObjectNameException e) {
            return new ErrorResultData("Malformed object name");
        } catch (UnsupportedDataTypeException e) {
            return new ErrorResultData(e.getLocalizedMessage());
        } catch (InstanceNotFoundException e) {
            return new ErrorResultData("No such object. Object name: " + e.getLocalizedMessage());
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
            LOGGER.debug("Converting result from OpenMBean data type");
            return convertOpenMBeanData(((OpenMBeanAttributeInfo) attributeInfo).getOpenType(), value);
        }
        else {
            LOGGER.debug("Converting result from MBean data type");
            return convertMBeanData(attributeInfo.getType(), value);
        }
    }

    @SuppressWarnings("unchecked")
    private ResultData convertOpenMBeanData(OpenType<?> type, Object value) throws UnsupportedDataTypeException {
        return OpenMBeanDataConverterFactory.INSTANCE.getConverter(type).convert(type, value);
    }

    @SuppressWarnings("unchecked")
    private ResultData convertMBeanData(String typeClassName, Object value) throws UnsupportedDataTypeException {
        return MBeanDataConverterFactory.INSTANCE.getConverter(typeClassName).convert(typeClassName, value);
    }
}

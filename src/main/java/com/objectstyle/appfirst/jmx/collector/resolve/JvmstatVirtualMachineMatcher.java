package com.objectstyle.appfirst.jmx.collector.resolve;

import com.sun.tools.attach.VirtualMachineDescriptor;
import sun.jvmstat.monitor.*;

import java.net.URISyntaxException;

public class JvmstatVirtualMachineMatcher extends StringInclusionVirtualMachineMatcher implements VirtualMachineMatcher {
    @Override
    protected String getVirtualMachineString(VirtualMachineDescriptor descriptor) {
        try {
            MonitoredHost monitoredHost = MonitoredHost.getMonitoredHost(new HostIdentifier((String) null));
            MonitoredVm monitoredVm = monitoredHost.getMonitoredVm(new VmIdentifier(descriptor.id()));
            return MonitoredVmUtil.jvmArgs(monitoredVm) + " "
                    + MonitoredVmUtil.jvmFlags(monitoredVm) + " " + MonitoredVmUtil.commandLine(monitoredVm);
        } catch (MonitorException e) {
            throw new VirtualMachineResolverRuntimeException("Error while trying while getting VM attributes through Monitor API", e);
        } catch (URISyntaxException e) {
            throw new IllegalArgumentException("Can't create VM identifier from provided VM descriptor");
        }
    }
}

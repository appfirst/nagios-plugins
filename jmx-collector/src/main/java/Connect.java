import com.objectstyle.appfirst.jmx.collector.utils.JVMAttach;
import sun.tools.jconsole.LocalVirtualMachine;

import javax.management.*;
import javax.management.remote.JMXConnector;
import javax.management.remote.JMXConnectorFactory;
import javax.management.remote.JMXServiceURL;
import java.io.IOException;
import java.util.Map;
import java.util.Set;

/**
 * Created with IntelliJ IDEA.
 * User: admin
 * Date: 9/9/12
 * Time: 4:58 PM
 * To change this template use File | Settings | File Templates.
 */
public class Connect {

	public static void main(String[] args) throws IOException {
		list();
	}

	private static void list() throws IOException {
		Map<Integer, LocalVirtualMachine> vms = LocalVirtualMachine.getAllVirtualMachines();
		for (LocalVirtualMachine lvm : vms.values()) {
			System.out.println(String.format("lvm.id = %d; lvm.displayName = %s, lvm.manageable = %b,lvm.attachable = %b", lvm.vmid(), lvm.displayName(), lvm.isManageable(), lvm.isAttachable()));
			JVMAttach attach = new JVMAttach();
			attach.setLvm(lvm);
			attach.attach();
			lvm = LocalVirtualMachine.getLocalVirtualMachine(lvm.vmid());
			getListBeans(lvm);
			System.out.println(String.format("lvm.id = %d; lvm.displayName = %s, lvm.manageable = %b,lvm.attachable = %b", lvm.vmid(), lvm.displayName(), lvm.isManageable(), lvm.isAttachable()));
		}
	}


	private static void getListBeans(LocalVirtualMachine lvm){
		try {
			JMXServiceURL jmxUrl = new JMXServiceURL(lvm.connectorAddress());
			JMXConnector jmxc = JMXConnectorFactory.connect(jmxUrl);

			MBeanServerConnection mbsc = jmxc.getMBeanServerConnection();

			Set<ObjectInstance> beans = mbsc.queryMBeans(null, null);

			String template = "%s.%s] -P -Dsolr -O %s -A %s";
			for (ObjectInstance instance : beans) {

				MBeanInfo beanInfo = mbsc.getMBeanInfo(instance.getObjectName());

				MBeanAttributeInfo[] attributes = beanInfo.getAttributes();
				for (MBeanAttributeInfo attributeInfo : attributes) {
					if (!attributeInfo.isWritable() &&
							!attributeInfo.getType().equals("java.util.Map"))
						System.out.println(String.format(template, instance.getObjectName().getKeyProperty("type"), attributeInfo.getName(), instance.getObjectName(), attributeInfo.getName()));
				}
			}
		} catch (Throwable e) {
			e.printStackTrace();
		}
	}
}


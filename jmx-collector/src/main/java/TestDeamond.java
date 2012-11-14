import java.util.Properties;

public class TestDeamond {

	public static void main(String[] args) {

		Runnable runnable = new Runnable() {
			@Override
			public void run() {
				while(true)
				{
					Properties properties = System.getProperties();
					properties.list(System.out);
					try {
						Thread.sleep(1000);
					} catch (InterruptedException e) {
						break;
					}
				}
			}
		};

		Thread thread = new Thread(runnable);
		thread.setDaemon(true);
		thread.run();

	}
}

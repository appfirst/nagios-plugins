package com.os.appfirst;

import static org.junit.Assert.*;

import java.util.ArrayList;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;


public class AppTest {
	ArrayList<Metric> metrics1 = new ArrayList<Metric>();
	static NagiosOutput nagiosOut = new NagiosOutput();

	@Before
	public void setUp() throws Exception {
		this.metrics1.add(
				new Metric(
						"METRIC_NAME",
						1,
						"METRIC_UNIT"
				)
		);
		
		this.metrics1.add(
				new Metric(
						"METRIC_NAME1",
						2,
						"METRIC_UNIT"
				)
		);
	}

	@After
	public void tearDown() throws Exception {
	}

	@Test
	public void testListOfMetricsAsArgument() {
		int argumentsCount = 2;
		String strMerics = "specific_metric_name1;specific_metric_name2;";
		String[] arrOfMetrics = strMerics.split(";"); 
		assertEquals("length", arrOfMetrics.length, argumentsCount);
		
		for(String s: arrOfMetrics){
			System.out.println("metric: " + s);
			ArrayList<Metric> metrics2 = new ArrayList<Metric>(); 
			metrics2.add(
					new Metric(
							s,
							1,
							"METRIC_UNIT"
					)
			);
			this.metrics1.addAll(metrics2);
			
		}
		
		System.out.println(this.metrics1);
		
		assertEquals("metrics size", this.metrics1.size(), argumentsCount * 2);
		
		String msg = nagiosOut.formatMetrics(this.metrics1);
		System.out.println(msg);
		assertNotNull(msg);
		
	}

}

package com.os.appfirst;

import java.util.ArrayList;

import org.apache.log4j.Logger;

//Plugin Return Code	Service State	Host State
//0	OK	UP
//1	WARNING	UP or DOWN/UNREACHABLE*
//2	CRITICAL	DOWN/UNREACHABLE
//3	UNKNOWN	DOWN/UNREACHABLE
public class NagiosOutput {
	static final Logger logger = Logger.getLogger(NagiosOutput.class);
	static final String baseNameOfMetric = "Oracle.DB";
	static final String sep = " : ";
	
	public NagiosOutput (){
		
	}
	
	public void echoOk(String msg){
		System.out.println(baseNameOfMetric + " OK" + sep + msg);
	}
	
	public void echoWarn(String msg){
		System.out.println(baseNameOfMetric + " WARNING" + sep + msg);
	}
	
	public void echoCritical(String msg){
		System.out.println(baseNameOfMetric + " CRITICAL" + sep + msg);
	}
	
	private String trimName(String name){
		return name.replace("(", "").replace(")", "").replace("%", "");
	}
	
	private String formatName(String name){
		return trimName(name).replace(" ", "_").toLowerCase();
	}

	public String formatMetrics(ArrayList<Metric> metrics) {
		if (metrics != null){
			String nOutput = "";
			String nPerfData = "";
			
			for(Metric m: metrics){
				nOutput += trimName(m.name) + " = " + m.val + ",";
				
			}
			
			nOutput = nOutput.substring(0, nOutput.length() - 1);
			
			for(Metric m: metrics){
				nPerfData += this.formatName(m.name) + "=" + m.val + " ";
			}
			nPerfData = nPerfData.substring(0, nPerfData.length() - 1);
			
			return nOutput + " | " + nPerfData;
		} else {
			return "List of metrics are NULL";
		}
	}
}

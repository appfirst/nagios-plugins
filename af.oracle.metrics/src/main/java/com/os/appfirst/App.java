package com.os.appfirst;

import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.Date;
import java.util.Properties;

import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.GnuParser;
import org.apache.commons.cli.Option;
import org.apache.commons.cli.OptionBuilder;
import org.apache.commons.cli.Options;
import org.apache.commons.cli.ParseException;
import org.apache.log4j.LogManager;
import org.apache.log4j.Logger;
import org.apache.log4j.PropertyConfigurator;


public class App {

	static Logger logger = Logger.getLogger(App.class);
	static OracleMetrics orcMetrics = null;
	static Log2File logOutput = null;
	static NagiosOutput nagiosOut = new NagiosOutput();
	
	
	private enum Metrics {
	    cpu, io, custom, sqls;
	}

	public static void main(String[] parameters) {
		parser(parameters);
	}
	
	private static void upLog4jConf(String level) { 
	    Properties props = new Properties();
	    String file = "/log4j.properties";

	    
	    try { 
	        InputStream configStream = App.class.getResourceAsStream(file); 
	        if (configStream != null){
	        	props.load(configStream); 
	        } else {
	        	System.out.println(file + " is null"); 
	        }
	        
	        configStream.close(); 
	    } catch (IOException e) { 
	        System.out.println("Error: Cannot laod configuration file "); 
	    } 

	    props.setProperty("log4j.rootLogger", level + " ,file"); 
	    LogManager.resetConfiguration(); 
	    PropertyConfigurator.configure(props); 
	 }


		
	public static Boolean parser(String[] parameters) {

		String oracleDbUrl = null;
		String msg = "Unknown error";
		ArrayList<Metric> metrics = new ArrayList<Metric>();
		
		 
		
		CommandLine commandLine;
		Option optVerbose= OptionBuilder.withArgName("verbose").hasArg().withDescription("verbose").create("V");
		Option optDBUrl = OptionBuilder.withArgName("dburl").hasArg().withDescription("Oracle Database path").create("D");
		Option optDBUser = OptionBuilder.withArgName("dbuser").hasArg().withDescription("Oracle Database user").create("U");
		Option optDBPass = OptionBuilder.withArgName("dbpass").hasArg().withDescription("Oracle Database password").create("P");
		Option optLogPath = OptionBuilder.withArgName("logpath").hasArg().withDescription("Path to output log file").create("L");
		Option optMetric = OptionBuilder.withArgName("metric").hasArg().withDescription("Common metric name to get").create("M");
		Option optDBInterval = OptionBuilder.withArgName("dbinterval").hasArg().withDescription("Interval/period to get list of SQLs").create("I");
		Option optSpecMetric = OptionBuilder.withArgName("smetric").hasArg().withDescription("Specific metric name to get").create("N");
		Option optTags = OptionBuilder.withArgName("tags").hasArg().withDescription("Enable tags").create("T");
		


		Options options = new Options();
		CommandLineParser parser = new GnuParser();
		
		
		options.addOption(optVerbose);
		options.addOption(optDBUrl);
		options.addOption(optDBUser);
		options.addOption(optDBPass);
		options.addOption(optLogPath);
		options.addOption(optMetric);
		options.addOption(optSpecMetric);
		options.addOption(optDBInterval);
		options.addOption(optTags);
		
		
		
		logger.debug("processing at " + new Date());

		try {
			commandLine = parser.parse(options, parameters);
			
//			if (commandLine.hasOption("V")){
//				upLog4jConf("debug");
//			} else {
//				upLog4jConf("fatal");
//			}
			
			
			if (commandLine.hasOption("D")) {
				
				if (commandLine.hasOption("U") && commandLine.hasOption("P")){
				
					oracleDbUrl = commandLine.getOptionValue("D");
					
					logger.debug("dbUrl is: " + oracleDbUrl);
					
					if (commandLine.hasOption("M") && commandLine.getOptionValue("M") != null) {
						
						String m = commandLine.getOptionValue("M");
						Metrics metric = Metrics.valueOf(m);
						
						orcMetrics = new OracleMetrics(oracleDbUrl, commandLine.getOptionValue("U"), commandLine.getOptionValue("P"));
						if (!orcMetrics.isConnected()){
							nagiosOut.echoCritical("Faild to connect to DB");
						}
						
						
						// check metric name
						switch(metric) {
						    case cpu:
						    	//orcMetrics.getSysStatMetrics();
						    	metrics = orcMetrics.getSysMetrics("CPU");
						    	msg = nagiosOut.formatMetrics(metrics);
						        break;
						        
						    case io:
						    	metrics = orcMetrics.getSysMetrics("I/O");
						    	msg = nagiosOut.formatMetrics(metrics);
						        break;
						        
						    case custom:
						    	if (commandLine.hasOption("N")) {
						    		String sm = commandLine.getOptionValue("N").trim().replace("\\", "");
						    		String[] arrOfMetrics = sm.split(";");
						    		ArrayList<Metric> tmpMetrics = new ArrayList<Metric>();
						    		
						    		for(String s: arrOfMetrics){
						    			
						    			tmpMetrics = orcMetrics.getSysMetrics(s);
						    			if (tmpMetrics !=null){
						    				metrics.addAll(tmpMetrics);
						    			}						
									}
						    		
							    	msg = nagiosOut.formatMetrics(metrics);
						    	} else {
						    		msg = "SpecificmMetric name not set.";
						    	}
						        break;
						        
						    case sqls:
						    	if (commandLine.hasOption("L")) {
						    		String p = commandLine.getOptionValue("L").trim();
									logger.debug("Default SQLs log output file path is " + p);
									logOutput = new Log2File(p);

								} else {
									String p = "af.oracle.log";
									logger.debug("using default log path " + p);
									logOutput = new Log2File(p);
								}
						    	
						    	String period = "5";
						    	if (commandLine.hasOption("I")) {
						    		period = commandLine.getOptionValue("I").trim();
						    		logger.debug("Using custom period for SQls query: " + period + "secs");
						    	}
						    	
						    	orcMetrics.setLogOutput(logOutput);
						    	String username = commandLine.getOptionValue("U").trim().toUpperCase();
						    	boolean tags = commandLine.hasOption("T");
						    	metrics = orcMetrics.getSqlList(username, period, tags);
						    	
						    	if (metrics != null) {
						    		msg = "Count of SQLs = " + metrics.size();
						    	} else {
						    		msg = "Error getting metrics";
						    		return false;
						    	}
						    	logOutput.close();
						    	
						        break;
						}
					

						
						nagiosOut.echoOk(msg);
						return true;
						
					} else {
						msg = "Metric name not set.";
					}
					
				} else {
					msg = "Oracle DB username and password not set.";
				}
			} else {
				msg = "Oracle DB url not set, you should specify it in format jdbc:oracle:thin:@[host name]:1521:[DB name] ";
			}
			
			
			nagiosOut.echoCritical(msg);
			logger.fatal(msg);
			
			


		} catch (ParseException exception) {
			msg = "Parse error: " + exception.getMessage();
			nagiosOut.echoCritical(msg);
			logger.fatal(msg);
		}
		return false;
	}
}

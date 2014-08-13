package com.os.appfirst;

import java.io.InputStream;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.Date;
import java.util.Properties;

import org.apache.commons.lang3.StringUtils;
import org.apache.log4j.Logger;

public class OracleMetrics {
	
	static final Logger logger = Logger.getLogger(App.class);
	static final OracleSqlQuerys sqlQ = new OracleSqlQuerys();
	private Properties prop = new Properties();
	private Log2File logOutput = null;
	private Boolean connected = false;
	
	
	public OracleMetrics(String dbUrl,String dbUser,String DbPass){
		this.readSqlsFromFile();
		if (sqlQ.connect(dbUrl, dbUser, DbPass)){
			connected = true;
		}
	
	}
	
	public Boolean isConnected(){
		return this.connected;
	}
	
	private Boolean readSqlsFromFile(){

        InputStream input = null;
        
		try {
			String filename = "sqls.xml";
    		input = this.getClass().getClassLoader().getResourceAsStream(filename);
    		if(input==null){
    			logger.error("Sorry, unable to find " + filename);
    		    return false;
    		}
 
    		prop.loadFromXML(input);
 
		} catch (Exception e) {
			logger.error("read SQL from file error: " + e.getMessage());
			return false;
		}
		
		
		return true;
	}
	
	private String[] getSql(String name){
		
		String tmp = this.prop.getProperty(name);
		return tmp.toString().split(";");

	}
	
	

	/**
	 *  V$SYSSTAT metrics
	 */
	public void getSysStatMetrics() {
		//		rs.getInt("class")
		//		1 - User
		//		2 - Redo
		//		4 - Enqueue
		//		8 - Cache
		//		16 - OS
		//		32 - Real Application Clusters
		//		64 - SQL
		//		128 - Debug

		String sql = "SELECT NAME, VALUE, CLASS FROM V$SYSSTAT WHERE NAME IN "
				+ "(  'parse time cpu', 'parse time elapsed','parse count (hard)', 'CPU used by this session', 'physical write bytes', 'physical read bytes')";
		ResultSet rs = sqlQ.makeQuery(sql);
		try {
			while (rs.next()) {
				logger.debug(rs.getString("name") + " " + rs.getInt("class") + ": " + rs.getInt("value"));
			}
		} catch (SQLException e) {
			logger.error("SQL error: " + e.getMessage());
		}
	}
	
	// AF_Select, AF_Insert, AF_Update, AF_Delete
	private String parseSqlType(String sql){
		sql = sql.toLowerCase();
		if (sql.indexOf("select") >= 0){
			return "_Select";
		} else if (sql.indexOf("alter") >= 0){
			return "_Alter";
		} else if (sql.indexOf("insert") >= 0){
			return "_Insert";
		} else if (sql.indexOf("update") >= 0){
			return "_Update";
		} else if (sql.indexOf("merge") >= 0){
			return "_Merge";
		} else if (sql.indexOf("truncate") >= 0){
			return "_Truncate";
		} else if (sql.indexOf("drop") >= 0){
			return "_Drop";
		}
		return "";
	}
	
	public String getTag(String sql){

		sql = ":AF_SQL" + parseSqlType(sql) + ":";
		return sql;
		
	}
	
	
	public ArrayList<Metric> getSqlList(String username, String period, boolean tags){

		String[] sqls = getSql("sql_list");
		ResultSet rs = null;
		ArrayList<Metric> metrics = new ArrayList<Metric>();

		String sql = StringUtils.join(sqls, "").trim();
		
		sql = sql.replace("[!PERIOD]", period);
		sql = sql.replace("[!USERNAME]", username);
		rs = sqlQ.makeQuery(sql);
		
		logger.debug(sql);
		if (rs == null){
			return null;
		}
		
		
		try {
			while (rs.next()) {
				
				long et =  rs.getInt("ELAPSED_TIME");
				long e =  rs.getInt("EXECUTIONS");
				String sqlText = rs.getString("SQL_TEXT").replace("\r", " ");
				
				if ( sqlText.length() > 150){
					sqlText = sqlText.substring(0, 150) + "...";
				}
				if (e > 0){
					
					String tag = "";
					if (tags) {
						tag = getTag(sqlText);
					}

					String res = tag + " [" + new Date() + "]" +
							//" " + rs.getString("SAMPLE_TIME") + 
							" id:" + rs.getString("SQL_ID") + 
							" last_acc: " + rs.getString("LAST_ACTIVE_TIME") + 
							" exec_time: " + et/e +
							" sql: " + sqlText;

					this.writeToLog(res);
//					@TODO SERVICE
					metrics.add(
							new Metric(
									rs.getString("SQL_ID"),
									rs.getInt("EXECUTIONS"),
									rs.getString("SAMPLE_TIME")
							)
					);
					
				}

				
			}
		} catch (SQLException e) {
			logger.error("SQL error: " + e.getMessage());
		}
		return metrics;
	}
	
	
	public ArrayList<Metric> getSysMetrics(String mName) {
		
		String[] sqls = getSql("sysmetric");
		ResultSet rs = null;
		ArrayList<Metric> metrics = new ArrayList<Metric>(); 
		
		String sql = StringUtils.join(sqls, "").trim();
		
		sql = sql.replace("[!LIKE]", mName);
		rs = sqlQ.makeQuery(sql);
		
		logger.debug("SQL: " + sql);
		
		try {
			while (rs.next()) {
				String res = rs.getString("METRIC_NAME") + " " + rs.getInt("VALUE") + ": " + rs.getString("METRIC_UNIT");
				logger.debug(res);
				this.writeToLog(res);
				metrics.add(
						new Metric(
								rs.getString("METRIC_NAME"),
								rs.getInt("VALUE"),
								rs.getString("METRIC_UNIT")
						)
				);
				
			}
		} catch (SQLException e) {
			logger.error("SQL error: " + e.getMessage());
		}
		return metrics;
	}
	
	private void writeToLog(String logStr){
		if (this.logOutput != null && logStr.length() > 0){
			this.logOutput.writeToFile( logStr); //new Date() + " " +
			
		}
		
	}


	public void setLogOutput(Log2File logOutput) {
		this.logOutput = logOutput;
		
	}
}

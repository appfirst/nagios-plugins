package com.os.appfirst;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;

import org.apache.log4j.Logger;

public class Log2File {
	static final Logger logger = Logger.getLogger(Log2File.class);
	public String outputFileName = null;
	private BufferedWriter bw = null;
	
	public Log2File(String outputFileName){
		this.outputFileName = outputFileName;
		
		File file = new File(this.outputFileName);
		try {
			if (!file.exists()) {
				file.createNewFile();
			}
	
			FileWriter fw;

			fw = new FileWriter(file.getAbsoluteFile(), true);
	
			this.bw = new BufferedWriter(fw);
		} catch (IOException e) {
			logger.fatal("writeToFile error: " + e.getMessage());
		}
	}
	
//	@TODO close file only when application done his tasks
	public void writeToFile(String str) {

		try {
			if (this.bw != null) {
				this.bw.write(str);
				this.bw.newLine();
			}
			
		} catch (IOException e) {
			logger.fatal("writeToFile error: " + e.getMessage());
		}

	}
	
	public void close() {
		try {
			if (this.bw != null) {
				this.bw.close();
			}
		} catch (IOException e) {
			logger.fatal("error closing BufferedWriter: " + e.getMessage());
		} 
	}

}

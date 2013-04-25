##	Check IMPI Sensors for use with AppFirst Polled Data under windows
##	clark@appfirst.com
##	requires that ipmiutil be installed.
##	http://ipmiutil.sourceforge.net/FILES/ipmiutil-2.9.0.msi
##      Polled Data Config Line:
##	command[sensor_fan]=c:\windows\system32\WindowsPowerShell\v1.0\powershell.exe "c:\Users\Administrator\ipmi\check_ipmi_sensors -t fan"
##
##  Note that on some systems, you may need to change the bios to enable "Plug & Play BMC Detection" or windows will not load
##   the IPMI driver
##
Param (
	[parameter(Mandatory=$false)]
	[alias("t")]
	[string]$sensor_type = "all",
	[parameter(Mandatory=$false)]
	[alias("c")]
	[string]$ipmi_command = "ipmiutil"
)

$env:path = $env:path + ";c:\program files (x86)\sourceforge\ipmiutil\"

if ($sensor_type -eq "all"){
	$ipmiutil_args = "sensor -c"
}
else{
	$ipmiutil_args = "sensor -c -g "+$sensor_type
}

$ipmi_command += " "+$ipmiutil_args

[Array]$ipmiutil_output = iex $ipmi_command

#$ipmiutil_output

if ($ipmiutil_output.length -lt 3){
	exit(3) 
}


if ($ipmiutil_output[2].Contains("Unrecognized")){
	exit(3)
}

if ($ipmiutil_output[2].Contains("Unrecognized")){
}


$status=0
 
for ($i=4; $i -lt $ipmiutil_output.length-1; $i++){
	$line = $ipmiutil_output[$i]
	if ($line.contains("invalid")){
		continue
	}

	[Array]$cols = $line.split("|")
	if ($cols[5].contains("warn") -and $status -lt 1){
		$status = 1
	}
	if ($cols[5].contains("crit") -and $status -lt 1){
		$status = 2
	}
}
switch ($status){
	0 {$ocw = "OK"}
	1 {$ocw = "WARNING"}
	2 {$ocw = "CRITICAL"}
}

$output = $sensor_type + " " + $ocw +" | "
for ($i=4; $i -lt $ipmiutil_output.length-1; $i++){
	$line = $ipmiutil_output[$i]
	if ($line.contains("invalid")){
		continue
	}
	[Array]$cols = $line.split("|")
	if ($cols[6] -ne ""){
		$sensor_name = $cols[4]
		$sensor_name = $sensor_name.trim()
		$sensor_name = $sensor_name -Replace " ", "_"
		$sensor_value = $cols[6]
		$sensor_value = $sensor_value.trim()
		$output += $sensor_name + "=" + $sensor_value + ";"
	}	
}


## now scrub the output
#replace multiple spaces with single
$output = $output -Replace "\s{2,}", ""
# remove units (to be nagios compliant)
$output = $output -Replace " RPM;", ";"
$output = $output -Replace " V;", ";"
$output = $output -Replace " C;", ";"
$output = $output -Replace " %;", ";"
# remove trailing ';' if present
$output = $output -Replace ";$", ""
# if no values were report, just status, we can deal with that.  Just leave off the '|'
$output = $output -Replace "\| $", ""

$output
exit ($status)
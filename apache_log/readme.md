App First apache access log statistic
=====================

A module parse apche access log files and calculates 
number of visitited urls and store that data in specifyed file,
by default af_apache_visited_urls.log in folder where script located.


* `python af_alogs.py -h` will detail configuration flags

to start daemon:
    `python af_alogs.py start --interval=60`
and to stop:
    `python af_alogs.py stop`

to get current state of daemon and count of urls:
    `python af_alogs.py status`



Configuration flags
-----------
`--interval` - interval in seconds to ask apache access logs about updates, by default 60 sec

`--apache-log-file-path` - Path to apache log file , by default `/var/log/apache2/access.log`

`--output-log-file-path` - Path to file where urls count will be saved, by default `af_apache_visited_urls.log`

`--tags` - Enable tags for log file, should be in format like :AF_TAG_NAME:
`--apache-host` - Apache hostname will be included in statsD counter name


Example
-----------
command example to use at "Polled Data Config"

    command[apache_log]=python /usr/share/appfirst/plugins/libexec/apache_log/af_alogs.py status
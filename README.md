Welcome to the **Log-Analytics** wiki!

In this big-data analytics project, I have developed a real-time web server log monitoring system using big data technologies. Below image shows the complete architecture of the project.

![Log Analysis Architecture](https://github.com/adsk261095/log-analysis/blob/master/Project_architecture.PNG)

For this project, I am using **Hortonworks Sandbox version 2.5**.

This project has Modules as follows:
* ## **Flume**
In this Flume module, there is a sparkstreamingflume.conf configuration file.
This configuration file has:

**Source** - Spool Directory where the log will be published by the webserver. This spool directory is being continuously monitored by Flume, for any new additions.

**Sink** - We have 2 sinks, first is the Spark Streaming Application where logs are being transferred using avro and analyzed in real-time. Second is the HDFS where logs are being dumped for historic records.
Since we have 2 sources, therefore we have 2 channels to which source is feeding the log data.

Command to run flume is as follows:

`flume-ng agent --name agent --conf conf --conf-file sparkstreamingflume.conf`

* ## **Spark Streaming Application**
Here Logs are being analyzed in real-time. The DStream are being read every one second.
The cumulative analysis of request and their status code is being done over a 1-minute window sliding every second.
This type of windowing methodology (similar to rolling mean analysis) provides a true overview of the realtime scenario.
Log Analysis information is being dumped into HBase every second.

To run the script first off all set:

`export SPARK_MAJOR_VERSION=2`

Then run the script using the command:

`spark-submit --packages org.apache.spark:spark-streaming-flume_2.11:2.0.0 SparkFlume.py`


* ## **HDFS**
Flume is also dumping Log into HDFS for keeping a historical record. Directory of format `%y-%m-%d/%H%M/%S` will be created. The log files are dumped in Sequence File Format. Since this file format has the benefit of storing all the metadata information corresponding to every record. Also, this file format is compatible with other technologies like Hive, Pig, Spark, etc which is a big plus for us.


* ## **Oozie**
Oozie is going to trigger the spark application at EOD., for that date's log file analysis.


* ## **Spark Application**
Spark application is going to read dated HDFS directory Sequence file and do request and status type analysis(as done by Spark Streaming Application). The result of the analysis is dumped by application into HBase corresponding to run date.

To run the script first off all set:

`export SPARK_MAJOR_VERSION=2`

Then run the script using the command:

`spark-submit  SparkHdfs.py`

'''
Author: Amandeep Singh
'''

'''
inorder to run it in Hortonworks 2.5
use the following:
export SPARK_MAJOR_VERSION=2
run using command:
spark-submit --packages org.apache.spark:spark-streaming-flume_2.11:2.0.0 SparkFlume.py
'''

import re

from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.flume import FlumeUtils

parts = [
    r'(?P<host>\S+)',                   # host %h
    r'\S+',                             # indent %l (unused)
    r'(?P<user>\S+)',                   # user %u
    r'\[(?P<time>.+)\]',                # time %t
    r'"(?P<request>.+)"',               # request "%r"
    r'(?P<status>[0-9]+)',              # status %>s
    r'(?P<size>\S+)',                   # size %b (careful, can be '-')
    r'"(?P<referer>.*)"',               # referer "%{Referer}i"
    r'"(?P<agent>.*)"',                 # user agent "%{User-agent}i"
]
pattern = re.compile(r'\s+'.join(parts)+r'\s*\Z')

'''
mapping each log to a tuple of (request, status)
So that we can analyse status of each request
'''
def extractURLRequestAndStatus(line):
    exp = pattern.match(line)
    if exp:
        status = exp.groupdict()["status"]
        request = exp.groupdict()["request"]
        if request:
           requestFields = request.split()
           if (len(requestFields) > 1):
                return (str(requestFields[1]), str(status))


if __name__ == "__main__":

    sc = SparkContext(appName="StreamingFlumeLogAggregator")
    sc.setLogLevel("ERROR")
    ssc = StreamingContext(sc, 1)

    flumeStream = FlumeUtils.createStream(ssc, "localhost", 9092)

    lines = flumeStream.map(lambda x: x[1])
    urls_status = lines.map(extractURLRequestAndStatus)

    # Reduce by URL over a 1-minute window sliding every second
    urlStatusCounts = urls_status.map(lambda x: (x, 1)).reduceByKeyAndWindow(lambda x, y: x + y, lambda x, y : x - y, 60, 1)

    # Sort and print the results
    sortedResults = urlStatusCounts.transform(lambda rdd: rdd.sortBy(lambda x: x[1], False))
    sortedResults.pprint()

    ssc.checkpoint("/home/maria_dev/spark/checkpoint")
    ssc.start()
    ssc.awaitTermination()

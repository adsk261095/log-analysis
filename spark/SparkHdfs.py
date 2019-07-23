'''
Author: Amandeep Singh
'''

'''
inorder to run it in Hortonworks 2.5
use the following:
export SPARK_MAJOR_VERSION=2
run using command:
spark-submit SparkHdfs.py
'''

import re

from pyspark import SparkContext

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
            # converted bytearray to string
                return (str(requestFields[1]), str(status))


if __name__ == "__main__":

    sc = SparkContext(appName="SparkHdfsLogAggregator")
    sc.setLogLevel("ERROR")

    logs = sc.sequenceFile('/user/maria_dev/logs/19-07-22/2020/00/')

    lines = logs.map(lambda x: x[1])
    urls_status = lines.map(extractURLRequestAndStatus)

    # Reduce by URL over a 5-minute window sliding every second
    urlStatusMapper = urls_status.map(lambda x: (x, 1))
    urlStatusReducer = urlStatusMapper.reduceByKey(lambda x, y: x + y)

    '''
    Sort and print the results in
    descending order of count
    '''
    sortedResults = urlStatusReducer.sortBy(lambda x: -x[1])
    print sortedResults.collect()

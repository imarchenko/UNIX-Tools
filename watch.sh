#!/bin/sh
# Tool to watch a data transfer into a directory

#./watch.sh <local DIR> <remote size of data in bytes>
#./watch.sh /data/TEST 98910334123

FULL_DATA_SIZE=$2

SLEEP_TIME=3
LAST_SIZE=`du -sb $1 | awk '{print $1}'`

TIME_LEFT_AVGS=Many

for (( i=0; 1; i++ )); do
    NEW_SIZE=`du -sb $1 | awk '{print $1}'`
    PERCENT=`echo $NEW_SIZE | awk '{print ($1/2159840996175)*100}'`
    RATE_BPS=`echo $NEW_SIZE $LAST_SIZE | awk '{print ($1-$2)/3}'`
    RATE_MBPS=`echo $RATE_BPS | awk '{print $1/1024/1024}'`

    TIME_LEFT=`echo $FULL_DATA_SIZE $NEW_SIZE $RATE_BPS | awk '{print (($1-$2)/$3)/60/60}'`

    if [[ $i -eq 0 ]]; then
        TIME_LEFT_REPORT=Unknown
    elif [[ $i -eq 1 ]]; then
        TIME_LEFT_REPORT=$TIME_LEFT
        TIME_LEFT_AVGS=$TIME_LEFT
    else
        TIME_LEFT_AVGS=`echo $TIME_LEFT_AVGS $TIME_LEFT | awk '{print $1+$2}'`
        TIME_LEFT_REPORT=`echo $TIME_LEFT_AVGS $i | awk '{print $1/$2}'`
    fi

    echo "${PERCENT}% ($RATE_MBPS MB/s) - $TIME_LEFT_REPORT hours left"

    LAST_SIZE=$NEW_SIZE

    sleep ${SLEEP_TIME}s
done;

#!/bin/bash

set -euo pipefail

sleep_time=$1
rollup_cache=`mktemp`

mkdir -p raw
while true; do
  date=`date +%s`
  echo processing at $date
  for procdir in `ls -d /proc/[0-9]*`; do
    pid=`basename $procdir`

    # Test whether we can access. File permissions, and hence `test -r`, lie.
    # Get contents of rollup once; I think this takes a fair bit of processing in-kernel
    if ! cat $procdir/smaps_rollup > $rollup_cache 2> /dev/null ; then continue; fi

    pss=`grep -E '^Pss:' $rollup_cache | awk '{print $2}'`
    rss=`grep -E '^Rss:' $rollup_cache | awk '{print $2}'`
    cmd=`head -n1 -z $procdir/cmdline | tr -d '\000' | awk '{print $1}'`
    echo $rss $pss $cmd >> raw/$date
  done
  sleep $sleep_time
done

#!/usr/bin/env python3

import csv
import os
import subprocess
import sys
import time

from collections import defaultdict


def get_mappings_for_pid(pid):
    try:
        pmap = subprocess.run(
                ['pmap', '-XX', str(pid)],
                text=True,
                check=True,
                capture_output=True)
    except subprocess.CalledProcessError:
        return {}

    lines = pmap.stdout.splitlines()
    cmd = ' '.join(lines[0].split()[1:])
    labels = lines[1].split()
    pss_idx = labels.index('Pss')
    rss_idx = labels.index('Rss')

    mappings = defaultdict(lambda: {'pss': 0, 'rss': 0})
    for mapline in lines[2:-2]:
        mapline = mapline.split()

        # There's not a great way to distinguish the (variable number of) flags
        # from the mapping name, which may not be present. Assume that if the
        # last field is 2-long, then it's actually one of the vmflags and there
        # is no mapping name.
        name = mapline[-1]
        if len(name) == 2:
            name = 'anon'

        pss = int(mapline[pss_idx])
        rss = int(mapline[rss_idx])

        #print(f'parsed pss:{pss} rss:{rss} name:{name}')

        mappings[(cmd, name)]['pss'] += pss
        mappings[(cmd, name)]['rss'] += rss

    return mappings

def get_mappings_for_pids(pids):
    # sequence of map of (cmd, name) to {'rss': x, 'pss': y}
    all_mappings = map(get_mappings_for_pid, pids)

    # merged map of (cmd, name) to {'rss': x, 'pss': y}
    merged_mappings = defaultdict(lambda: {'pss': 0, 'rss': 0})
    for mappings in all_mappings:
        for ((cmd, name), mapping) in mappings.items():
            merged_mappings[(cmd, name)]['pss'] += mapping['pss']
            merged_mappings[(cmd, name)]['rss'] += mapping['rss']

    return merged_mappings

def get_pids():
    pmap = subprocess.run(
            ['ps', 'x', '-o', 'pid'],
            text=True,
            check=True,
            capture_output=True)
    return map(int, pmap.stdout.splitlines()[1:])

def log_current_usage(dirname):
    pids = get_pids()
    mappings = get_mappings_for_pids(get_pids())
    unix_seconds = int(time.time_ns()/1000000000)

    f = open(os.path.join(dirname, str(unix_seconds)), 'w')
    csv_writer = csv.writer(f)
    for ((cmd, name), mapping) in mappings.items():
        csv_writer.writerow([mapping['pss'],mapping['rss'],cmd,name])
    f.close()

if __name__ == '__main__':
    dirname = sys.argv[1]
    sleep_time = int(sys.argv[2])

    os.mkdir(dirname)

    while True:
        log_current_usage(dirname)
        time.sleep(sleep_time)

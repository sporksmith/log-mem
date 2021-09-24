#!/usr/bin/env python3

import csv
import itertools
import os
import subprocess
import sys
import time

from collections import defaultdict
from collections import namedtuple
from typing import NamedTuple

class MemMapping(NamedTuple):
    time: int
    cmd: str
    name: str
    pss: int
    rss: int

def merge(mappings):
    merged_mappings = []
    key_fn = lambda m: (m.time, m.cmd, m.name)
    mappings = mappings[:]
    mappings.sort(key=key_fn)
    for (mtime, cmd, name), group in itertools.groupby(mappings, key_fn):
        #group = list(group)
        #print(len(group))
        merged_mappings.append(
                MemMapping(
                    time=mtime,
                    cmd=cmd,
                    name=name,
                    pss=sum([m.pss for m in group]),
                    rss=sum([m.rss for m in group])))
    return merged_mappings

def get_mappings_for_pid(pid, time):
    try:
        pmap = subprocess.run(
                ['pmap', '-XX', str(pid)],
                universal_newlines=True,
                check=True,
                stdout=subprocess.PIPE)
    except subprocess.CalledProcessError:
        return []

    lines = pmap.stdout.splitlines()
    cmd = ' '.join(lines[0].split()[1:])
    labels = lines[1].split()
    pss_idx = labels.index('Pss')
    rss_idx = labels.index('Rss')
    flags_and_mapping_idx = labels.index('VmFlagsMapping')

    mappings = []
    for mapline in lines[2:-2]:
        # Split, but careful not to split last field, VmFlagsMapping
        mapline = mapline.split(None, len(labels) - 1)

        pss = int(mapline[pss_idx])
        rss = int(mapline[rss_idx])

        flags_and_mapping = mapline[flags_and_mapping_idx]
        name = mapline[flags_and_mapping_idx].split('  ')[1]

        mapping = MemMapping(time=time, cmd=cmd, name=name, pss= pss, rss= rss)
        mappings.append(mapping)

    return merge(mappings)

def get_mappings_for_pids(pids):
    unix_seconds = int(time.time())

    all_mappings = map(lambda pid: get_mappings_for_pid(pid, unix_seconds), pids)

    # flatten
    all_mappings = [val for sublist in all_mappings for val in sublist]

    return merge(all_mappings)

def get_pids():
    pmap = subprocess.run(
            ['ps', 'x', '-o', 'pid'],
            universal_newlines=True,
            check=True,
            stdout=subprocess.PIPE)
    return map(int, pmap.stdout.splitlines()[1:])

def log_current_usage():
    pids = get_pids()
    mappings = get_mappings_for_pids(get_pids())

    #csv_writer = csv.writer(sys.stdout)
    csv_writer = csv.DictWriter(sys.stdout, ['time', 'cmd', 'name', 'pss', 'rss'])
    csv_writer.writeheader()
    for mapping in mappings:
        csv_writer.writerow(mapping._asdict())
    sys.stdout.flush()

if __name__ == '__main__':
    sleep_time = int(sys.argv[1])

    while True:
        log_current_usage()
        time.sleep(sleep_time)
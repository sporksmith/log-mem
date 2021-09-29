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
    size: int
    pss: int
    rss: int
    referenced: int

def merge(mappings):
    merged_mappings = []
    key_fn = lambda m: (m.time, m.cmd, m.name)
    mappings = mappings[:]
    mappings.sort(key=key_fn)
    for (mtime, cmd, name), group in itertools.groupby(mappings, key_fn):
        group = list(group)
        merged_mappings.append(
                MemMapping(
                    time=mtime,
                    cmd=cmd,
                    name=name,
                    size=sum([m.size for m in group]),
                    pss=sum([m.pss for m in group]),
                    rss=sum([m.rss for m in group]),
                    referenced=sum([m.referenced for m in group]),
                    ))
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
    try:
        labels = lines[1].split()
    except:
        return []

    size_idx = labels.index('Size')
    pss_idx = labels.index('Pss')
    rss_idx = labels.index('Rss')
    referenced_idx = labels.index('Referenced')
    flags_and_mapping_idx = labels.index('VmFlagsMapping')

    mappings = []
    for mapline in lines[2:-2]:
        # Split, but careful not to split last field, VmFlagsMapping
        mapline = mapline.split(None, len(labels) - 1)

        size = int(mapline[size_idx])
        pss = int(mapline[pss_idx])
        rss = int(mapline[rss_idx])
        referenced = int(mapline[referenced_idx])

        flags_and_mapping = mapline[flags_and_mapping_idx]
        name = mapline[flags_and_mapping_idx].split('  ')[1]

        mapping = MemMapping(time=time, cmd=cmd, name=name, size=size, pss= pss, rss= rss, referenced=referenced)
        mappings.append(mapping)

    # Clear the 'referenced' bit
    try:
        with open(f'/proc/{pid}/clear_refs', 'w') as clear_refs:
            clear_refs.write('1')
    except:
        print(f'warning: couldn\'t clear refs for pid {pid}', sys.stderr)

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

if __name__ == '__main__':
    sleep_time = int(sys.argv[1])

    csv_writer = csv.DictWriter(sys.stdout, ['time', 'cmd', 'name', 'size', 'pss', 'rss', 'referenced'])
    csv_writer.writeheader()
    while True:
        pids = get_pids()
        mappings = get_mappings_for_pids(get_pids())

        for mapping in mappings:
            csv_writer.writerow(mapping._asdict())
        sys.stdout.flush()
        time.sleep(sleep_time)

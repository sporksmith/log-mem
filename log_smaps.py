#!/usr/bin/env python3

import sys
import os
import subprocess

from collections import defaultdict


def mappings_for_pid(pid):
    pmap = subprocess.run(
            ['pmap', '-XX', str(pid)],
            text=True,
            check=True,
            capture_output=True)
    lines = pmap.stdout.splitlines()
    cmd = ' '.join(lines[0].split()[1:])
    labels = lines[1].split()
    pss_idx = labels.index('Pss')
    rss_idx = labels.index('Rss')

    print(f'pss_idx: {pss_idx}')
    print(f'rss_idx: {rss_idx}')

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

        print(f'parsed pss:{pss} rss:{rss} name:{name}')

        mappings[(cmd, name)]['pss'] += pss
        mappings[(cmd, name)]['rss'] += rss

    return mappings

def mappings_for_pids(pids):
    # sequence of map of (cmd, name) to {'rss': x, 'pss': y}
    all_mappings = map(mappings_for_pid, pids)

    # merged map of (cmd, name) to {'rss': x, 'pss': y}
    merged_mappings = defaultdict(lambda: {'pss': 0, 'rss': 0})
    for mappings in all_mappings:
        for ((cmd, name), mapping) in mappings.items():
            merged_mappings[(cmd, name)]['pss'] += mapping['pss']
            merged_mappings[(cmd, name)]['rss'] += mapping['rss']

    return merged_mappings

if __name__ == '__main__':
    sleep_time = int(sys.argv[1])
    print('hello')

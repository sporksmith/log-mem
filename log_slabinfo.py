#!/usr/bin/env python3

import csv
import sys
import time

from typing import NamedTuple

class SlabInfo(NamedTuple):
    time: int
    name: str
    active_objs: int
    num_objs: int
    objsize: int

def get_slabinfos(time):
    slabinfos = []
    with open('/proc/slabinfo') as slabinfo:
        version_header = slabinfo.readline()
        # Maybe compare with specific version number, but yolo for now
        assert(version_header.startswith('slabinfo - version'))

        field_headers = slabinfo.readline().split()
        name_idx = field_headers.index('name') - 1
        active_objs_idx = field_headers.index('<active_objs>') - 1
        num_objs_idx = field_headers.index('<num_objs>') - 1
        objsize_idx = field_headers.index('<objsize>') - 1

        for line in slabinfo.readlines():
            line = line.split()
            slabinfos.append(SlabInfo(
                time=time,
                name=line[name_idx],
                active_objs=int(line[active_objs_idx]),
                num_objs=int(line[num_objs_idx]),
                objsize=int(line[objsize_idx])))

    return slabinfos

if __name__ == '__main__':
    sleep_time = int(sys.argv[1])

    csv_writer = csv.DictWriter(sys.stdout, ['time', 'name', 'active_objs', 'num_objs', 'objsize'])
    csv_writer.writeheader()

    while True:
        slabinfos = get_slabinfos(int(time.time()))
        for slabinfo in slabinfos:
            csv_writer.writerow(slabinfo._asdict())
        sys.stdout.flush()

        time.sleep(sleep_time)

#!/usr/bin/env python3

import sys
import os
import matplotlib.pyplot as plt

times = os.listdir('raw')
times = list(map(int, times))
times.sort()
#print(times)

psses = {}
for i in range(len(times)):
    cmds = {}
    for line in open(os.path.join('raw', str(times[i]))):
        rss,pss,cmd = line.strip().split(' ')
        cmd_psses = psses.setdefault(cmd, [])
        cmd_psses.extend([0] * (i - len(cmd_psses) + 1))
        cmd_psses[-1] += int(pss)

#        record = cmds.get(cmd, {'rss': 0, 'pss': 0})
#        record['rss'] += int(rss)
#        record['pss'] += int(pss)
#        d[cmd] = record
#    times[t] = d

#    for cmd,record in cmds.items():
#        print(f'{record["rss"]} {record["pss"]} {cmd}')

times = list(map(lambda x: x - times[0], times))

# filter to top N
total_psses = []
for cmd, cmd_psses in psses.items():
    total_psses.append((cmd, sum(cmd_psses)))
total_psses.sort(key=lambda x: x[1], reverse=True)
top_cmds = set(map(lambda x: x[0], total_psses[:10]))


for cmd, cmd_psses in psses.items():
    if cmd not in top_cmds:
        continue
    cmd_psses.extend([0] * (len(times) - len(cmd_psses)))
    plt.plot(times, cmd_psses, label=cmd)

plt.legend()
plt.show()

#print(times)
#print(psses)

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

# Get list sorted by total "integral" of pss over time
total_psses = []
for cmd, cmd_psses in psses.items():
    total_psses.append((cmd, sum(cmd_psses)))
total_psses.sort(key=lambda x: x[1], reverse=True)

# Plot top 10
for (cmd, total) in total_psses[:10]:
    # zero-extend, to handle commands that were no longer alive at end
    cmd_psses = psses[cmd]
    cmd_psses.extend([0] * (len(times) - len(cmd_psses)))

    # plot the line for this command
    plt.plot(times, cmd_psses, label=cmd)

# Render the plot
plt.legend()
plt.xlabel('seconds')
plt.ylabel('PSS KB')
plt.show()

#print(times)
#print(psses)

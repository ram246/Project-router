'''
Plot ping RTTs over time
'''
import os, sys
from helper import *
import plot_defaults

from matplotlib.ticker import MaxNLocator
from pylab import figure

parser = argparse.ArgumentParser()
parser.add_argument('--files', '-f',
                    help="Ping output files to plot",
                    required=True,
                    action="store",
                    nargs='+')

parser.add_argument('--freq',
                    help="Frequency of pings (per second)",
                    type=float,
                    default=10)

parser.add_argument('--type', '-t',
                    help="Determines if it is a ping plot or download plot",
                    default="ping")

parser.add_argument('--out', '-o',
                    help="Output png file for the plot.",
                    default=None) # Will show the plot

args = parser.parse_args()

def parse_ping(fname):
    ret = []
    lines = open(fname).readlines()
    num = 0
    for line in lines:
        if 'bytes from' not in line:
            continue
        try:
            rtt = line.split(' ')[-2]
            rtt = rtt.split('=')[1]
            rtt = float(rtt)
            ret.append([num, rtt])
            num += 1
        except:
            break
    return ret

def parse_download(fname):
    ret = []
    lines = open(fname).readlines()
    num = 0
    for line in lines:
        if line == '':
            continue
        try:
            down_time = float(line)
            # Compute time that download starts
            if num == 0:
                time = 0
            else:
                # 2 seconds in between downloads (freq = 0.5 := 1 download every 2 sec)
                interval_time = 1 / args.freq
                # Curr_time = prev_time + interval_time + duration of prev download
                time = ret[num - 1][0] + interval_time + ret[num - 1][1]
            
            ret.append([time, down_time])
            num += 1
        except:
            break
    return ret

m.rc('figure', figsize=(16, 6))
fig = figure()
ax = fig.add_subplot(111)
for i, f in enumerate(args.files):
    if args.type == 'ping':
        data = parse_ping(f)
        xaxis = map(float, col(0, data))
        start_time = xaxis[0]
        xaxis = map(lambda x: (x - start_time) / args.freq, xaxis)
    elif args.type == 'download':
        data = parse_download(f)
        xaxis = map(float, col(0, data))    
    if len(data) == 0:
        print >>sys.stderr, "%s: error: no ping data"%(sys.argv[0])
        sys.exit(1)

    qlens = map(float, col(1, data))

    ax.scatter(xaxis, qlens, lw=2)
    ax.xaxis.set_major_locator(MaxNLocator(4))

if args.type == 'ping':
    plt.ylabel("RTT (ms)")
elif args.type == 'download':
    plt.ylabel("Download time (ms)")

plt.grid(True)

if args.out:
    plt.savefig(args.out)
else:
    plt.show()

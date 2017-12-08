import requests
import time
import threading
import argparse
import numpy as np
import sys

count = 0
output = 0
lock = threading.Lock()

all_count = 0;
all_time = 0;

def add_count():
    global count
    lock.acquire()
    try:
        count += 1
    finally:
        lock.release()


def decrease_count(end,start):
    global count
    global output
    global all_count
    global all_time
    lock.acquire()
    try:
        count -= 1
        output += 1
        all_count = all_count + 1
        all_time = all_time + end-start
    finally:
        lock.release()


class SingleThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        add_count()
        index = int(1000 * np.random.rand())
        start = int(round(time.time() * 1000))
        requests.get("http://104.155.97.211/") 
        end = int(round(time.time() * 1000))
        decrease_count(end,start)
        print("%s,%s" % (start, (end-start)))
       
       


class CountThread(threading.Thread):
    def __init__(self, args):
        threading.Thread.__init__(self)
        self.args = args
        self.dur = args.mon_duration

    def run(self):
        qlen = []
        outputs = []
        global count
        global output
        while self.dur > 0:
            timestamp = int(round(time.time() * 1000))
            qlen.append([timestamp, count])
            outputs.append([timestamp, output])
            time.sleep(self.args.resolution)
            self.dur -= 1

        f = open('qfile.txt', 'w')
        for item in qlen:
            f.write("%s\n" % item)
        f.close()
        f = open('output.txt', 'w')
        for item in outputs:
            f.write("%s\n" % item)
        f.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='client generator')
    parser.add_argument("--load", default=0.001, type=float, help="traffic load")
    parser.add_argument("--duration", default=60, type=int, help="generating duration")
    parser.add_argument("--mon_duration", default=60, type=int, help="monitoring duration")
    parser.add_argument("--resolution", default=1, type=float, help="monitoring interval")
    parser.add_argument("--start_load", default=0.001, type=float, help="start load")
    args = parser.parse_args()

    interval = 1/args.load
    init = 1/args.start_load
    dur = args.duration*1000
    maxdur = dur

    cthread = CountThread(args)
    cthread.start()
    start = int(round(time.time() * 1000))
    print("%s,0" % start)

    while dur > 0:
        s = SingleThread()
        s.start()
        if (maxdur-dur) < 50*1000:
            intv = np.random.exponential(init)
        else:
            intv = np.random.exponential(interval)
        time.sleep(intv/1000)
        dur -= intv
    enddur = 10*1000
    while enddur > 0:
        s = SingleThread()
        s.start()
        intv = np.random.exponential(init)
        time.sleep(intv/1000)
        enddur -= intv

    print("All_count = %s, All_time = %s, Avg_time = %s" % (all_count, all_time,all_time/all_count*1.0))

#!/usr/bin/env python3

import datetime
import math
import subprocess
import time


def benchmark(opt, benchmark):
    subprocess.check_output(["./build.sh", "-O{opt}".format(opt=opt)])
    start = datetime.datetime.now()
    subprocess.check_output(["./bin/main.elf", 
                     "defs/benchmark{b}.csv".format(b=benchmark),
                     "output/benchmark"])
    return (datetime.datetime.now()-start).total_seconds()

def main():
    
    for opt in range(4):
        timings = [ ]
        for bm in range(3):
            score = benchmark(opt, bm)
            n = 10240000 if bm > 0 else 640000 
            timings.append(score/(n*math.pi*0.25))
        print("{opt}:".format(opt=opt), timings)

main()



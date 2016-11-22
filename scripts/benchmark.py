#!/usr/bin/env python3

import datetime
import math
import subprocess
import time

def read():
    subprocess.check_output(["git", "checkout", "./benchmark.txt"])
    print('Previous result:')
    with open('benchmark.txt') as bf:
        print(bf.read())

def benchmark(opt, benchmark):
    subprocess.check_output(["./build.sh", "-O{opt}".format(opt=opt)])
    start = datetime.datetime.now()
    subprocess.check_output(["./bin/main.elf", 
                     "defs/benchmark{b}.csv".format(b=benchmark),
                     "output/benchmark"])
    return (datetime.datetime.now()-start).total_seconds()

def main():
    read()
    print('\nCurrent result:')
    with open('benchmark.txt', 'w') as bf:
        for opt in range(4):
            timings = [ ]
            for bm in range(3):
                score = benchmark(opt, bm)
                n = 10240000 if bm > 0 else 640000 
                timings.append(score/(n*math.pi*0.25))
            print("%s: %.4g, %.4g, %.4g" % 
                    (opt, timings[0], timings[1], timings[2]))
            bf.write("%s: %.4g, %.4g, %.4g" % 
                    (opt, timings[0], timings[1], timings[2]))

main()



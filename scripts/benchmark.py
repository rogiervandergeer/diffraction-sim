#!/usr/bin/env python3

import datetime
import math
from subprocess import check_output
import pandas as pd
import time

def read():
    check_output(["git", "checkout", "./benchmark.txt"])
    print('Previous result:')
    with open('benchmark.txt') as bf:
        print(bf.read())

def read_result(filename):
    return pd.read_csv(filename, 
                       names=['block_id', 'col_id', 'row_id', 'x', 'y'])

def compare(file_1, file_2):
    df_1 = read_result(file_1)
    df_2 = read_result(file_2)
    df_m = df_1.merge(df_2, on=['block_id', 'col_id', 'row_id'], 
                      how='inner', suffixes=['_1', '_2'])
    if len(df_1) != len(df_2) or len(df_1) != len(df_m):
        raise Exception('Size and/or index mismatch!')
    df_m['x'] = abs(df_m['x_1'] - df_m['x_2'])
    df_m['y'] = abs(df_m['y_1'] - df_m['y_2'])
    changed = df_m[(df_m.x > 1E-3) | (df_m.y > 1E-3)]
    if len(changed) > 0:
        print(changed.head())
        raise Exception('Result does not match!')

def build(optimisation=0):
    check_output(['./build.sh', '-O{opt}'.format(opt=optimisation)])

def benchmark(benchmark):
    start = datetime.datetime.now()
    check_output(['./bin/main.elf', 
                  'defs/benchmark{b}.csv'.format(b=benchmark),
                  'output/benchmark{b}.csv'.format(b=benchmark)])
    sec = (datetime.datetime.now()-start).total_seconds()
    compare('reference/benchmark{b}.csv'.format(b=benchmark),
            'output/benchmark{b}.csv'.format(b=benchmark))
    return sec

def main():
    read()
    print('\nCurrent result:')
    with open('benchmark.txt', 'w') as bf:
        for opt in range(4):
            build(opt)
            timings = [ ]
            for bm in range(3):
                score = benchmark(bm)
                n = 10240000 if bm > 0 else 640000 
                timings.append(score/(n*math.pi*0.25))
            print("%s: %.4e, %.4e, %.4e" % 
                    (opt, timings[0], timings[1], timings[2]))
            bf.write("%s: %.4e, %.4e, %.4e\n" % 
                    (opt, timings[0], timings[1], timings[2]))

main()



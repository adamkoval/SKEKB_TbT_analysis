"""
Script for analysing synchronisation of BPMs from phase data (output from measure_optics.py).
This script outputs a text file discribing the number of turns each BPM is out of synch by.

Created on Thu Oct 18 14:56:32 2018
Edited on Fri May 24
Author: Adam Koval
"""
from __future__ import print_function
import sys
import os
import numpy as np
import argparse
from func import phase, phasetot

# Argument parser.
parser = argparse.ArgumentParser()
parser.add_argument('--phase_output_dir', '-pod',
                    dest="pod",
                    action="store")
parser.add_argument('--async_output_dir', '-aod',
                    dest="aod",
                    action="store")
parser.add_argument('--axis', '-ax',
                    dest="axis",
                    action="store")
args = parser.parse_args()

# Check if phase output directory exists, if not, exit.
if not os.path.exists(args.pod):
    print("Directory", args.pod, "not found.")
    sys.exit()
# Check if output dir for the present script exists, if not, create one.
if not os.path.exists(args.aod):
    os.system("mkdir " + args.aod)

# Check for asynchronous BPMs in each measurement reun using phase output.
for run in os.listdir(args.pod):
    datapath = args.pod + run + '/'
    try:
        S, names, deltaph, phx, phxmdl, Qx, Qy = phase(datapath, args.axis)
    except IOError:
        continue
    deltaphtot = phasetot(datapath, args.axis)

    level = []
    for i in range(len(deltaphtot)):
        if deltaphtot[i] / Qx >= .5:
            level.append('-1')
        elif deltaphtot[i] / Qx <= -.5:
            level.append('+1')
        elif deltaphtot[i] / Qx > -.5 and deltaphtot[i] / Qx < .5:
            level.append('0')
    file = open(args.aod + run + '.txt', 'w')
    file.write('{\n')
    g = 0
    try:
        for i in range(len(names)):
            if g != 0:
                file.write(',\n')
            file.write('"' + names[i] + '"->' + level[i])
            g += 1
    except IndexError:
        print(run)
        print(len(level))
        print(len(deltaphtot))
    file.write('\n}')
    file.close()

sys.exit()

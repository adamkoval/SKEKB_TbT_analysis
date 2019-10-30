"""
Script to plot frequency analysis output.

Author: Jacqueline Keintzel
Date: 29/10/2019
"""

from __future__ import print_function
from optparse import OptionParser
import numpy as np 
import matplotlib.pyplot as plt
import os
# import sys
# sys.path.append('/afs/cern.ch/work/j/jkeintze/public/Beta-Beat.src/Python_Classes4MAD')
# import metaclass
from func import read_bpms


def read_spectrum(file):
    """
    Reads amps or freqs file and returns all entries.
    """
    vals = []
    with open(file) as fo:
        lines = fo.readlines()[3:]
    fo.close()

    for j in range(len(lines[0].split())):
        vals = vals + [float(lines[i].split()[j]) for i in range(len(lines))]

    return np.array(vals)


def get_model_tunes(twiss):
    with open(twiss) as fo:
        lines = fo.readlines()
    Qx = float(lines[9].split()[3]) - np.trunc(float(lines[9].split()[3]))
    Qy = float(lines[10].split()[3]) - np.trunc(float(lines[10].split()[3]))

    return Qx, Qy

if __name__ == "__main__":

    fix = 10
    fiy = 3.5
    size = 20
    
    parser = OptionParser()
    parser.add_option("-s", "--sdds",  dest="sdds", help="Folder of sdds files, leads to other folders.", action="store")
    parser.add_option("-m", "--model",  dest="model", help="Model folder to get the twiss model for the tunes.", action="store")
    parser.add_option("-a", "--axis",  dest="axis", help="Transverse plane, either x or y.", action="store")
    parser.add_option("-p", "--pngpdf",  dest="pngpdf", help="Format of plot.", action="store")
    (options, args) = parser.parse_args()

    all_sdds = [sd for sd in os.listdir(options.sdds) if 'sdds' in sd]
    harmonic_output = os.path.join(options.sdds[:-15], 'unsynched_harmonic_output')
    model = os.path.join(options.model, 'twiss.dat')

    Qx, Qy = get_model_tunes(model)
    

    for sdds in all_sdds[1:2]:
        amp = read_spectrum(os.path.join(harmonic_output, sdds+'.amps'+options.axis))
        freq = read_spectrum(os.path.join(harmonic_output, sdds+'.freqs'+options.axis))
    

    num=1
    plt.figure(num, figsize=(fix, fiy))
    plt.scatter(1-freq, amp*1e3, s=5, marker='o')
    plt.plot(np.array([Qx, Qx]), np.array([1e-10, 1e10]), ls='--', color = 'orange', lw = 2)
    plt.plot(np.array([Qy, Qy]), np.array([1e-10, 1e10]), ls='--', color = 'orange', lw = 2)
    plt.xlabel('Fractional Tune [-]', fontsize=size)
    plt.ylabel('Amplitude [mm]', fontsize=size)
    plt.tick_params('both', labelsize=size)
    plt.yscale('log')
    plt.ylim(5e2*min(amp*1e3), 1.3*max(amp*1e3))
    plt.xlim(0.5, max(1-freq))
    plt.tight_layout()
    plt.savefig(options.sdds+'../FrequencySpectrum_'+options.axis+'.'+options.pngpdf)
    plt.close(num)
    num=num+1

    plt.figure(num, figsize=(fix, fiy))
    plt.scatter(1-freq, amp*1e3, s=5, marker='o')
    plt.plot(np.array([Qx, Qx]), np.array([1e-10, 1e10]), ls='--', color = 'orange', lw = 2)
    plt.plot(np.array([Qy, Qy]), np.array([1e-10, 1e10]), ls='--', color = 'orange', lw = 2)
    plt.xlabel('Fractional Tune [-]', fontsize=size)
    plt.ylabel('Amplitude [mm]', fontsize=size)
    plt.tick_params('both', labelsize=size)
    plt.yscale('log')
    plt.ylim(5e2*min(amp*1e3), 1.3*max(amp*1e3))
    # plt.ylim(5e2*min(amp/(max(amp))), 1.3)
    plt.tight_layout()
    plt.xlim(Qx-0.01, Qx+0.01)
    plt.savefig(options.sdds+'../FrequencySpectrum_QxZoom_'+options.axis+'.'+options.pngpdf)
    plt.close(num)
    num=num+1

    plt.figure(num, figsize=(fix, fiy))
    plt.scatter(1-freq, amp*1e3, s=5, marker='o')
    plt.plot(np.array([Qx, Qx]), np.array([1e-10, 1e10]), ls='--', color = 'orange', lw = 2)
    plt.plot(np.array([Qy, Qy]), np.array([1e-10, 1e10]), ls='--', color = 'orange', lw = 2)
    plt.xlabel('Fractional Tune [-]', fontsize=size)
    plt.ylabel('Amplitude [mm]', fontsize=size)
    plt.tick_params('both', labelsize=size)
    plt.yscale('log')
    plt.ylim(5e2*min(amp*1e3), 1.3*max(amp*1e3))
    # plt.ylim(5e2*min(amp/(max(amp))), 1.3)
    plt.tight_layout()
    plt.xlim(Qy-0.01, Qy+0.01)
    plt.savefig(options.sdds+'../FrequencySpectrum_QyZoom_'+options.axis+'.'+options.pngpdf)
    plt.close(num)
    num=num+1

    

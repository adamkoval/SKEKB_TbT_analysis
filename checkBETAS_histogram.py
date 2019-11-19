
"""
Script to plot histograms of beta-beating before and after
BPM calibration.

Author: Jacqueline Keintzel
Date: 24/10/2019
"""

from __future__ import print_function
from optparse import OptionParser
import matplotlib.pyplot as plt
import os
import numpy as np
#from func import read_bet_phase


def read_bet_phase(folder, plane):
    """
    Reads beta_phase_*.tfs and returns the beta function.
    """
    file = os.path.join(folder, 'beta_phase_' + plane + '.tfs')
    with open(file) as fo:
        lines = fo.readlines()[15:]
    fo.close()
    beta_beat = [float(lines[i].split()[10]) for i in range(len(lines))]
    beta_beat_err = [float(lines[i].split()[11]) for i in range(len(lines))]
    bpms = [lines[i].split()[0] for i in range(len(lines))]
    return beta_beat, beta_beat_err, bpms




if __name__ == "__main__":

    fix = 10
    fiy = 4.5
    size = 20

    parser = OptionParser()
    parser.add_option("-s", "--sdds",  dest="sdds", help="Folder of sdds files.", action="store")
    parser.add_option("-o", "--phase",  dest="phase", help="Folder of phase output files.", action="store")
    parser.add_option("-a", "--axis",  dest="axis", help="Transverse plane, either x or y.", action="store")
    parser.add_option("-w", "--when",  dest="when", help="Before or after calibration.", action="store")
    parser.add_option("-p", "--pngpdf",  dest="pngpdf", help="Format of plot.", action="store")
    (options, args) = parser.parse_args()


    all_sdds = [sd for sd in os.listdir(options.sdds) if 'sdds' in sd]

    beta_beat_arr = []
    beta_beat_err_arr = []
    for sdds in all_sdds:
        folder = os.path.join(options.phase, sdds)

        beta_beat, beta_beat_err, bpms = read_bet_phase(folder, options.axis)
        beta_beat_arr = beta_beat_arr +  [100*beta_beat[i] for i in range(len(beta_beat)) if 100*beta_beat[i] < 100]
        beta_beat_err_arr = beta_beat_err_arr +  [100*beta_beat_err[i] for i in range(len(beta_beat_err)) if 100*beta_beat[i] < 100]
        
    av_beta_beat = np.mean(beta_beat_arr)
    av_beta_beat_err = np.mean(beta_beat_err_arr)


    plt.figure(1, figsize=(fix, fiy))
    n, bins, patches  = plt.hist(beta_beat_arr, bins=100)
    plt.plot(np.array([av_beta_beat,av_beta_beat]), np.array([0,max(n)]), ls='--', color = 'grey', lw = 2)
    plt.ylim(0, max(n))
    plt.tick_params('both', labelsize=size)
    if options.axis == 'x': plt.xlabel(r'$\Delta \beta_{x, ph}$ [%]', fontsize=size)
    else: plt.xlabel(r'$\Delta \beta_{y, ph}$ [%]', fontsize=size)
    plt.ylabel('Counts', fontsize=size)
    plt.tight_layout()
    plt.savefig(options.sdds+'../BetaBEAT_'+options.when+'_'+options.axis+'.'+options.pngpdf)
    plt.close(1)

    plt.figure(2, figsize=(fix, fiy))
    n, bins, patches  = plt.hist(beta_beat_err_arr, bins=50)
    plt.plot(np.array([av_beta_beat_err,av_beta_beat_err]), np.array([0,max(n)]), ls='--', color = 'grey', lw = 2)
    plt.ylim(0, max(n))
    plt.tick_params('both', labelsize=size)
    if options.axis == 'x': plt.xlabel(r'$STD \Delta \beta_{x, ph}$ [%]', fontsize=size)
    else: plt.xlabel(r'$STD \Delta \beta_{y, ph}$ [%]', fontsize=size)
    plt.ylabel('Counts', fontsize=size)
    plt.tight_layout()
    plt.savefig(options.sdds+'../BetaBEATERR_'+options.when+'_'+options.axis+'.'+options.pngpdf)
    plt.close(2)


"""
Script to plot orbit data from sdds files.

Author: Jacqueline Keintzel
Date: 19/11/2019
"""

from __future__ import print_function
from optparse import OptionParser
import numpy as np 
import matplotlib.pyplot as plt
import os



if __name__ == "__main__":

    fix = 10
    fiy = 3.5
    size = 20
    
    parser = OptionParser()
    parser.add_option("-s", "--sdds",  dest="sdds", help="Folder of sdds files, leads to other folders.", action="store")
    parser.add_option("-p", "--pngpdf",  dest="pngpdf", help="Format of plot.", action="store")
    (options, args) = parser.parse_args()

    all_sdds = [sd for sd in os.listdir(options.sdds) if 'sdds' in sd]

    num=1
    for sdds in all_sdds:
        print(sdds)
        with open(os.path.join(options.sdds, sdds)) as fo:
            lines = fo.readlines()[11:]
        fo.close()

        for ll in range(len(lines)):
            axis = 'x' if lines[ll].split()[0] == '0' else 'y'
            bpm = lines[ll].split()[1]
            print(bpm)
            orbit = [ float(lines[ll].split()[(3+i)]) for i in range(len(lines[ll].split()[3:])) if (lines[ll].split()[(3+i)] != '0') ]
            turns = np.array(range(len(orbit)))
            plt.figure(num, figsize=(fix, fiy))
            plt.scatter(turns, orbit, s=5, marker='o')
            plt.xlabel('Turn Number [-]', fontsize=size)
            plt.ylabel('Orbit [mm]', fontsize=size)
            plt.tick_params('both', labelsize=size)
            plt.xlim(0,len(turns)-1)
            plt.tight_layout()
            plt.savefig(os.path.join(options.sdds, str(sdds[:-5])+'_'+str(bpm)+'_'+str(axis)+'.'+options.pngpdf))
            plt.close(num)
            num=num+1
        
        #quit()
            
        
    

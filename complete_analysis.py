"""
Main script which allows the user to utilise desired
functions of this analysis package.

Author: Adam Koval
Date: 18/7/2019
With essential contributions from
Andreas Wegscheider, Renjun Yang & Paul Thrane.
"""
from __future__ import print_function
import argparse
import os
import sys

from func import read_pathnames, sdds_conv, harmonic_analysis, phase_analysis, asynch_analysis, asynch_cmap

parser = argparse.ArgumentParser()
required = parser.add_argument_group('required arguments')
required.add_argument('--pathnames',
                    action='store',
                    dest='pathnames',
                    help='Path to pathnames.txt file, which contains all other paths necessary for this script.')

parser.add_argument('--debug', '-db',
                    nargs='?',
                    const='2',
                    help='Debug option. Only runs for specified number of files as opposed to all. Default is set to 2.')
parser.add_argument('--group_runs', '-group',
                    action='store_true',
                    help='To be used when multiple runs for a single setting are available.')
parser.add_argument('--harmonic1', '-h1',
                    action='store_true',
                    help='Harmonic analysis without knowledge of BPM synch. This is enough to obtain tunes.')
parser.add_argument('--phase1', '-p1',
                    action='store_true',
                    help='Phase analysis of harmonic1 output without BPM synch knowledge.')
parser.add_argument('--plotasynch1', '-pa1',
                    action='store_true',
                    help='Plotting of BPM synchronisation from phase1 output, before synch fix is applied.')
parser.add_argument('--asynch', '-aa',
                    action='store_true',
                    help='Analysis of BPM synchronisation from phase1 output.')
parser.add_argument('--harmonic2', '-h2',
                    action='store_true',
                    help='sdds conversion and harmonic analysis with knowledge of BPM synch.')
parser.add_argument('--phase2', '-p2',
                    action='store_true',
                    help='Phase analysis of harmonic2 output with knowledge of BPM synch.')
parser.add_argument('--plotasynch2', '-pa2',
                    action='store_true',
                    help='Plotting of BPM synchronisation from phase2 output, after synch fix is applied.')
parser.add_argument('--omc3', '-o3',
                    action='store_true',
                    help='Use the new OMC3-analysis instead of python2-BetaBeat.src.')
args = parser.parse_args()

# Read in destinations
pathnames = read_pathnames(args.pathnames)

# Inputs from study
nturns = pathnames["nturns"]
ringID = pathnames["ringID"]
lattice = pathnames["lattice"]
input_data = pathnames["input_data_path"]
kickax = pathnames["kickax"]

# For BetaBeat.src
model_path = pathnames["model_path"]

# For present code
main_output = pathnames["main_output_path"]
if not os.path.exists(main_output):
    os.system('mkdir ' + main_output)
else:
    pass
unsynched_sdds = main_output + pathnames["unsynched_sdds_path"]
synched_sdds = main_output + pathnames["synched_sdds_path"]
file_dict = pathnames["file_dict"]

# Executables
gsad = pathnames["gsad"]

# Output directories
synched_harmonic_output = main_output + "synched_harmonic_output/"
synched_phase_output = main_output + "synched_phase_output/"
unsynched_harmonic_output = main_output + "unsynched_harmonic_output/"
unsynched_phase_output = main_output + "unsynched_phase_output/"


if args.omc3 == True:
    py_version = 3
    python_exe = pathnames["python3_exe"]
    BetaBeatsrc_path = pathnames["omc3_path"]
else: 
    py_version = 2
    python_exe = pathnames["python_exe"]
    BetaBeatsrc_path = pathnames["BetaBeatsrc_path"]

# Warning about -group flag
if args.group_runs == True:
    while True:
        user_input = input('"--group_runs" flag has been switched on. Please note that the script WILL misbehave if this flag is used incorrectly. Refer to README Sec. IV.I for more info.\nDo you wish to proceed? (y/n):')
        if user_input == 'y':
            break
        elif user_input == 'n':
            print('Aborting.')
            sys.exit()
        else:
            print('Please enter a valid input ("y" or "n").')
            continue


# First sdds conversion and harmonic analysis 1
if args.harmonic1 == True:
    sdds_conv(input_data, file_dict, main_output, unsynched_sdds,
              lattice, gsad, ringID, args.debug, kickax, asynch_info=False)

    harmonic_analysis(py_version, python_exe, BetaBeatsrc_path, model_path,
                      unsynched_harmonic_output, unsynched_sdds,
                      nturns, str(0.04), lattice, gsad)
else:
    pass


# Phase analysis 1
if args.phase1 == True:
    phase_analysis(py_version, python_exe, BetaBeatsrc_path, model_path,
                   unsynched_harmonic_output, unsynched_phase_output, unsynched_sdds, args.group_runs)
else:
    pass


# Asynch analysis
if args.asynch == True:
    asynch_analysis(python_exe, unsynched_phase_output, main_output)


# Plotting BPM synchronisation pre-fix
if args.plotasynch1 == True:
    asynch_cmap(python_exe, unsynched_sdds, unsynched_phase_output, when='before')


# Second sdds conversion (with knowledge of BPM synch) and harmonic analysis 2
if args.harmonic2 == True:
    sdds_conv(input_data, file_dict, main_output, synched_sdds,
              lattice, gsad, ringID, args.debug, kickax, asynch_info=True)

    harmonic_analysis(py_version, python_exe, BetaBeatsrc_path, model_path,
                      synched_harmonic_output, synched_sdds,
                      nturns, str(0.04), lattice, gsad)
else:
    pass


# Phase analysis 2
if args.phase2 == True:
    phase_analysis(py_version, python_exe, BetaBeatsrc_path, model_path,
                   synched_harmonic_output, synched_phase_output, synched_sdds, args.group_runs)
else:
    pass


# Plotting BPM synchronisation post-fix
if args.plotasynch2 == True:
    asynch_cmap(python_exe, synched_sdds, synched_phase_output, when='after')

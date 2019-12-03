"""
Main script which allows the user to utilise desired
functions of this analysis package.

Author: Jacqueline Keintzel , Adam Koval
Date: 25/11/2019
With essential contributions from
Andreas Wegscheider, Renjun Yang & Paul Thrane.
"""
from __future__ import print_function
import argparse
import os
import sys

# from func import read_pathnames, sdds_conv, harmonic_analysis, phase_analysis, asynch_analysis, asynch_cmap, bpm_calibration, calib_hist, freq_spec
from func import read_pathnames, sdds_conv, harmonic_analysis, phase_analysis, asynch_analysis
from func import asynch_cmap, bpm_calibration, calib_hist, freq_spec, chromatic_analysis
from func import plot_optics, coupling_analysis, sdds_turns, cut_large_sdds

parser = argparse.ArgumentParser()
required = parser.add_argument_group('required arguments')
required.add_argument('--pathnames',
                    action='store',
                    dest='pathnames',
                    help='Path to pathnames.txt file, which contains all other paths necessary for this script.')

parser.add_argument('--debug', '-db',
                    action='store_true',
                    help='Debug option. Runs analysis only for one file and disables some warnings.')
parser.add_argument('--group_runs', '-g',
                    action='store_true',
                    help='To be used when multiple runs for a single setting are available.')
parser.add_argument('--all_at_once', '-all',
                    action='store_true',
                    help='To be used when all files should run at once, e.g. for dispersion measurement with off-momentum files.')
parser.add_argument('--harmonic1', '-h1',
                    action='store_true',
                    help='Harmonic analysis without knowledge of BPM synch. This is enough to obtain tunes.')
parser.add_argument('--plotsdds1', '-ps1',
                    action='store_true',
                    help='Plotting of raw sdds files.')        
parser.add_argument('--plotfreq1', '-pf1',
                    action='store_true',
                    help='Plotting of frequency spectrum.')
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
parser.add_argument('--plotoptics2', '-po2',
                    action='store_true',
                    help='Plots the optics repository after BPM synchronisation.')
parser.add_argument('--plotasynch2', '-pa2',
                    action='store_true',
                    help='Plotting of BPM synchronisation from phase2 output, after synch fix is applied.')
parser.add_argument('--calib', '-c',
                    action='store_true',
                    help='Calculates the BPM calibration for this measurement.')
parser.add_argument('--phase3', '-p3',
                    action='store_true',
                    help='Phase analysis of harmonic3 output with knowledge of BPM calibration.')
parser.add_argument('--plotcalib1', '-pc1',
                    action='store_true',
                    help='Plotting of BPM calibration from phase2 output, before calibration is applied.')
parser.add_argument('--plotcalib2', '-pc2',
                    action='store_true',
                    help='Plotting of BPM calibration from phase3 output, after calibration is applied.')
parser.add_argument('--omc3', '-o3',
                    action='store_true',
                    help='Use the new OMC3-analysis instead of python2-BetaBeat.src.')
args = parser.parse_args()

# Read in destinations
pathnames = read_pathnames(args.pathnames)

# Inputs from study
nturns = pathnames["nturns"]
ringID = pathnames["ringID"].lower()
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
unsynched_sdds = os.path.join(main_output, 'unsynched_sdds/')
synched_sdds = os.path.join(main_output, 'synched_sdds/')
file_dict = pathnames["file_dict"]

# Executables
gsad = pathnames["gsad"]

# Output directories
calibrated_harmonic_output = os.path.join(main_output, 'calibrated_harmonic_output/')
calibrated_phase_output = os.path.join(main_output, 'calibrated_phase_output/')
synched_harmonic_output = os.path.join(main_output, 'synched_harmonic_output/')
synched_phase_output = os.path.join(main_output, 'synched_phase_output/')
unsynched_harmonic_output = os.path.join(main_output, 'unsynched_harmonic_output/')
unsynched_phase_output = os.path.join(main_output, 'unsynched_phase_output/')


if args.omc3 == True:
    py_version = 3
    python_exe = pathnames["python3_exe"]
    BetaBeatsrc_path = pathnames["omc3_path"]
else: 
    py_version = 2
    python_exe = pathnames["python_exe"]
    BetaBeatsrc_path = pathnames["BetaBeatsrc_path"]

# Warning about -group flag
if args.debug is not True:
    if (args.group_runs or args.all_at_once) == True:
        while True:
            user_input = input('"--group_runs" and/or "--all_at_once" ' 
                'flag has been switched on. Please note that the script WILL misbehave' 
                'if this flag is used incorrectly. Refer to README Sec. IV.I for more info.\n'
                'Do you wish to proceed? (y/n):"')
            if user_input == 'y':
                break
            elif user_input == 'n':
                print('Aborting.')
                sys.exit()
            else:
                print('Please enter a valid input ("y" or "n").')
                continue
else:
    print(" ********************************************\n",
                "Debug option is on:\n",
                '"Some warnings are disabled, so please be careful."\n',
                "********************************************")


# First sdds conversion and harmonic analysis 1
if args.harmonic1 == True:
    sdds_conv(input_data, file_dict, main_output, unsynched_sdds,
              lattice, gsad, ringID, args.debug, kickax, asynch_info=False)

    cut_large_sdds(python_exe, unsynched_sdds, file_dict)

    harmonic_analysis(py_version, python_exe, BetaBeatsrc_path, model_path,
                      unsynched_harmonic_output, unsynched_sdds,
                      nturns, str(0.04), lattice, gsad)
else: pass

if args.plotsdds1 == True:
    sdds_turns(python_exe, unsynched_sdds)
else: pass

if args.plotfreq1 == True:
    freq_spec(python_exe, unsynched_sdds, model_path)
else: pass

# Phase analysis 1
if args.phase1 == True:
    phase_analysis(py_version, python_exe, BetaBeatsrc_path, model_path,
                   unsynched_harmonic_output, unsynched_phase_output, unsynched_sdds, 
                   ringID, args.group_runs, args.all_at_once)
    try: chromatic_analysis(model_path, unsynched_phase_output)         
    except: pass
else: pass


# Asynch analysis
if args.asynch == True:
    asynch_analysis(python_exe, unsynched_phase_output, main_output, model_path, ringID)
else: pass


# Plotting BPM synchronisation pre-fix
if args.plotasynch1 == True:
    asynch_cmap(python_exe, unsynched_sdds, unsynched_phase_output, when='before')
else: pass


# Second sdds conversion (with knowledge of BPM synch) and harmonic analysis 2
if args.harmonic2 == True:
    sdds_conv(input_data, file_dict, main_output, synched_sdds,
              lattice, gsad, ringID, args.debug, kickax, asynch_info=True)

    cut_large_sdds(python_exe, synched_sdds, file_dict)

    harmonic_analysis(py_version, python_exe, BetaBeatsrc_path, model_path,
                      synched_harmonic_output, synched_sdds,
                      nturns, str(0.04), lattice, gsad)
else: pass


# Phase analysis 2
if args.phase2 == True:
    phase_analysis(py_version, python_exe, BetaBeatsrc_path, model_path,
                   synched_harmonic_output, synched_phase_output, synched_sdds, 
                   ringID, args.group_runs, args.all_at_once)
    try: chromatic_analysis(model_path, synched_phase_output)    
    except: pass
    try: coupling_analysis(model_path, synched_sdds, synched_harmonic_output, synched_phase_output, args.all_at_once)
    except: pass
else: pass

if args.plotoptics2 == True:
    plot_optics(python_exe, synched_phase_output, model_path, ringID)
else: pass

# Plotting BPM synchronisation post-fix
if args.plotasynch2 == True:
    asynch_cmap(python_exe, synched_sdds, synched_phase_output, when='after')
else: pass


# Plotting BPM calibration pre-calib
if args.plotcalib1 == True:
    calib_hist(python_exe, synched_sdds, synched_phase_output, when='before')
else: pass


# Calculation of BPM calibration and writing lin files and calib harmonic folder
if args.calib == True:
    bpm_calibration(python_exe, synched_sdds, synched_harmonic_output, synched_phase_output,
                    calibrated_harmonic_output, calibrated_phase_output, ringID)
else: pass


# Phase analysis 3, with calibrated BPMs
if args.phase3 == True:
    phase_analysis(py_version, python_exe, BetaBeatsrc_path, model_path,
                   calibrated_harmonic_output, calibrated_phase_output, synched_sdds, 
                   ringID, args.group_runs, args.all_at_once)
    try: chromatic_analysis(model_path, calibrated_phase_output)
    except: pass
else: pass


# Plotting BPM calibration post-calib
if args.plotcalib2 == True:
    calib_hist(python_exe, synched_sdds, calibrated_phase_output, when='after')
else: pass


print(" ********************************************\n",
        "Everything comes to an end at some point...\n",
        "Complete analysis is finished.\n",
        "********************************************")



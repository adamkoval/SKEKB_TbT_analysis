# =======================================
# Author: Adam Koval
# Date: 18/7/2019
# With essential contributions from 
# Andreas Wegscheider, Renjun Yang & Paul Thrane.
# =======================================
from __future__ import print_function
import argparse
import os

from func import read_pathnames, sdds_conv, harmonic_analysis, phase_analysis, asynch_analysis, asynch_cmap

parser = argparse.ArgumentParser()
parser.add_argument('--debug', '-db',
                    action='store_true')
parser.add_argument('--pathnames',
                    action='store',
                    dest='pathnames')
parser.add_argument('--harmonic1', '-h1',
                    action='store_true')
parser.add_argument('--phase1', '-p1',
                    action='store_true')
parser.add_argument('--asynch', '-a',
                    action='store_true')
parser.add_argument('--plotasynch1', '-pa1',
                    action='store_true')
parser.add_argument('--harmonic2', '-h2',
                    action='store_true')
parser.add_argument('--phase2', '-p2',
                    action='store_true')
parser.add_argument('--plotasynch2', '-pa2',
                    action='store_true')
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
BetaBeatsrc_path = pathnames["BetaBeatsrc_path"]
model_path = pathnames["model_path"]

# For present code
main_output = pathnames["main_output_path"]
if not os.path.exists(main_output):
    os.system('mkdir ' + main_output)
else:
    pass
unsynched_sdds = pathnames["unsynched_sdds_path"]
synched_sdds = pathnames["synched_sdds_path"]
file_dict = pathnames["file_dict"]

# Executables
gsad = pathnames["gsad"]
python_exe = pathnames["python_exe"]

# Output directories
synched_harmonic_output = main_output + "synched_harmonic_output/"
synched_phase_output = main_output + "synched_phase_output/"
unsynched_harmonic_output = main_output + "unsynched_harmonic_output/"
unsynched_phase_output = main_output + "unsynched_phase_output/"

# SDDS conversion

#asynch_info = False
sdds_conv(input_data, file_dict, main_output, unsynched_sdds,
          lattice, gsad, ringID, args.debug, kickax, asynch_info=False)

if args.harmonic1 == True:
    harmonic_analysis(python_exe, BetaBeatsrc_path, model_path,
                      unsynched_harmonic_output, unsynched_sdds,
                      nturns, str(0.04), lattice, gsad)
else:
    pass


if args.phase1 == True:
    phase_analysis(python_exe, BetaBeatsrc_path, model_path,
                   unsynched_harmonic_output, unsynched_phase_output, unsynched_sdds)
else:
    pass


if args.asynch == True:
    asynch_analysis(python_exe, unsynched_phase_output, main_output)


if args.plotasynch1 == True:
    asynch_cmap(python_exe, unsynched_sdds, unsynched_phase_output, when='before')


if args.harmonic2 == True:
    sdds_conv(input_data, file_dict, main_output, synched_sdds,
              lattice, gsad, ringID, args.debug, kickax, asynch_info=True)

    harmonic_analysis(python_exe, BetaBeatsrc_path, model_path,
                      synched_harmonic_output, synched_sdds,
                      nturns, str(0.04), lattice, gsad)
else:
    pass


if args.phase2 == True:
    phase_analysis(python_exe, BetaBeatsrc_path, model_path,
                   synched_harmonic_output, synched_phase_output, synched_sdds)
else:
    pass

if args.plotasynch2 == True:
    asynch_cmap(python_exe, synched_sdds, synched_phase_output, when='after')


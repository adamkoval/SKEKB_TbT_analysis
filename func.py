from __future__ import print_function
import os
import re
import numpy as np
import sys
from subprocess import Popen
import time

# ====================================================
# To be used in complete_analysis.py
# ====================================================
def look_for_dict(file_dict):
    """
    Checks for the presence of the dict file.
    NOTE: This function does not check the format of the dictionary!
    """
    if os.path.exists(file_dict):
        print('Dictionary file has been found.')
        return True
    else:
        print('You have not provided a dictionary file.')
        return False


def read_pathnames(pathnames):
    """
    Reads specifically the file 'pathnames.txt'
    and returns a dictionary with the assigned values.
    """
    with open(pathnames) as f:
        lines = f.readlines()
    lines = [line for line in lines if line[0] != '#']

    pathnames = {}
    for line in lines:
        line = line.split()
        pathnames[line[0]] = ' '.join(line[2:])

    return pathnames


def generic_dict(input_data_dir, file_dict, ringID):
    """
    Creates a generic file_dict.txt file given
    only the input data files and the ring for which one
    wishes to create a file_dict.txt.
    """
    files = []
    for file in os.listdir(input_data_dir):
        if file.endswith('.data') and file.startswith(ringID):
            files.append(file)

    fd = open(file_dict, 'w')
    fd.write('{\n')
    for i, file in enumerate(files):
        before = input_data_dir + file
        after = file[:-5] + '.sdds'
        if files[i] != files[-1]:
            fd.write('    {"' + before + '", "' + after + '"},\n')
        else:
            fd.write('    {"' + before + '", "' + after + '"}\n')
    fd.write('}\n')
    fd.close()


def check_path(path):
    """
    Check if path exists and is empty.
    Only return 'True' if both conditions satisfied.
    """
    if os.path.exists(path):
        if os.listdir(path):
            return True
        else:
            return False
    else:
        return False


def sdds_conv(input_data_dir, file_dict, main_output_dir, sdds_dir,
              lattice, gsad, ringID, debug, kickax, asynch_info):
    """
    KEK datafile -> sdds conversion.
    Function generates a SAD script which does the conversion, and then calls it.
    """
    def do_stuff():
        if debug == True:
            loopend = '2'
        else:
            loopend = 'Length[runs]'
        if asynch_info == False:
            fn = 'prerun.sad'
        else:
            fn = 'run.sad'
        LINE = get_LINE(lattice, gsad)
        file = open(fn, "w")
        file.write('FFS;\n'
                   'GetMAIN["' + lattice + '"];\n'
                   '\n'
                   'FFS["USE ' + LINE + '"],\n'
                   'CELL; CALC;\n'
                   'emit;\n\n'
                   'Get["func.n"];\n\n'
                   'runs = Get["' + file_dict + '"];\n'
                   'Do[\n'
                   '    fnr1 = "./"//runs[i, 1];\n')
        if asynch_info == False:
            file.write('    fbpm = "None";\n')
        elif asynch_info == True:
            file.write('    fbpm = "' + main_output_dir + 'outofphase' + kickax + '/"//runs[i, 2]//".txt";\n')
        file.write('    fwt1 = "' + sdds_dir + '"//runs[i, 2];\n'
                   '    Print["Converting "//runs[i, 1]//" -> "//runs[i, 2]];\n'
                   '    FormatBPMRead[fnr1, fwt1, fbpm];\n'
                   '    ,{i, 1, ' + loopend + '}];\n'
                   '\n'
                   'abort;\n')
        file.close()

        os.system(gsad + " " + fn)
        return print(" ********************************************\n",
                     "sdds_conv:\n",
                     '"' + fn + ' finished, sdds files can be found in ' + sdds_dir + '."\n',
                     "********************************************")
    while True:
        if look_for_dict(file_dict) == True:
            break
        else:
            user_input = raw_input('There is no dictionary file present for .data -> .sdds conversion. Would you like to create a new one (input -> create) or would you like to provide one (input -> provide)?\n')
            if user_input == 'create':
                generic_dict(input_data_dir, file_dict, ringID)
                continue
            elif user_input == 'provide':
                continue
    if os.path.exists(sdds_dir):
        # Checking if it is empty
        if os.listdir(sdds_dir):
            while True:
                user_input = raw_input(sdds_dir + ' directory contains files. Would you like to clean the directory and start from scratch? (options: yes, no, show contents)\n')
                if user_input == 'yes':
                    os.system('rm -r ' + sdds_dir + '*')
                    do_stuff()
                    break
                elif user_input == 'no':
                    break
                elif user_input == 'show contents':
                    os.system('ls ' + sdds_dir)
                    continue
                else:
                    print('Please enter a valid string (see "options").')
                    continue
        else:
            do_stuff()
    else:
        os.system("mkdir " + sdds_dir)
        do_stuff()


def get_LINE(lattice, gsad):
    """
    Function to extract name of LINE in lattice file.
    """
    with open(lattice) as f:
        lines = f.readlines()
    for line in lines:
        if line.split()[0] == 'LINE':
            LINE = re.match('LINE\s([A-Z]+)\s*\=', line).group(1)
    return LINE


def guess_tune(lattice, gsad):
    """
    Function generates and executes SAD script to obtain initial
    guesses for x & y tunes.
    """
    LINE = get_LINE(lattice, gsad) 
    fn = 'tune_info.sad'
    file = open(fn, "w")
    file.write('FFS;\n\n'
               'GetMAIN["' + lattice + '"];\n'
               'USE ' + LINE + ';\n'
               'CELL;\n'
               'CALC;\n\n'
               'file = OpenWrite["tune_guess.txt"];\n'
               'WriteString[file, "Qx = ", Twiss["nx", $$$]/(2*Pi), "\\n"];\n'
               'WriteString[file, "Qy = ", Twiss["ny", $$$]/(2*Pi), "\\n"];\n'
               'Close[file];\n'
               '\n'
               'abort;\n')
    file.close()
    os.system(gsad + ' ' + fn)
    return print(" ********************************************\n",
                 "guess_tunes:\n",
                 '"' + fn + ' finished, tune guesses are written to tune_guess.txt."\n',
                 "********************************************")


def harmonic_analysis(python_exe, BetaBeatsrc_path, model_path,
                      harmonic_output_path, sdds_path, nturns,
                      tune_range, lattice, gsad):
    """
    Function to call hole_in_one.py script from BetaBeat.src.
    """
    guess_tune(lattice, gsad)
    with open('tune_guess.txt') as f:
        lines = f.readlines()
    model_tunex = lines[0].split()[2]
    model_tuney = lines[1].split()[2]
    model_tunex = '0.' + re.match('[0-9]+\.([0-9]+)', model_tunex).group(1)
    model_tuney = '0.' + re.match('[0-9]+\.([0-9]+)', model_tuney).group(1)
#    model_tunex = str('{:.3g}'.format(float('0.' + re.match('[0-9]+\.([0-9]+)', model_tunex).group(1))))
#    model_tuney = str('{:.3g}'.format(float('0.' + re.match('[0-9]+\.([0-9]+)', model_tuney).group(1))))
#    model_tunex = '{:.3g}'.format(model_tunex)
#    model_tuney = '{:.3g}'.format(model_tuney)
    if not os.path.exists(harmonic_output_path):
        os.system('mkdir ' + harmonic_output_path)
    sdds_files = os.listdir(sdds_path)
    for i, run in enumerate(sdds_files):
        start = time.time()
        print(" ********************************************\n",
              "harmonic analysis:\n",
              '"Working on file ' + str(i) + '/' + str(len(sdds_files)) + ': ' + str(run) + '"\n',
              "********************************************")
        p = Popen([python_exe,
                   BetaBeatsrc_path + 'hole_in_one.py',
                   '--file', sdds_path + run,
                   '--outputdir', harmonic_output_path,
                   '--model', model_path + 'twiss.dat',
                   '--startturn', '2',
                   '--endturn', nturns,
                   'harpy',
                   '--harpy_mode', 'bpm',
                   '--tunex=' + model_tunex,
                   '--tuney=' + model_tuney,
                   '--nattunex=' + model_tunex,
                   '--nattuney=' + model_tuney,
                   '--tolerance=' + tune_range,
                   '--tune_clean_limit=1e-4']) # changed from 1e-5 to 10e-5 so that fewer BPMs are cleaned
        p.wait()
        finish = time.time() - start
        timer(i, len(sdds_files), finish)
    return print(" ********************************************\n",
                 "harmonic analysis:\n",
                 '"Harmonic analysis finished."\n',
                 "********************************************")


def phase_analysis(python_exe, BetaBeatsrc_path, model_path,
                   harmonic_output_path, phase_output_path, sdds_path):
    """
    Function to call measure_optics.py script from BetaBeat.src.
    """
    if not os.path.exists(phase_output_path):
        os.system('mkdir ' + phase_output_path)
    sdds_files = os.listdir(sdds_path)
    for i, run in enumerate(sdds_files):
        start = time.time()
        print(" ********************************************\n",
              "phase analysis:\n",
              '"Working on file ' + str(i) + '/' + str(len(sdds_files)) + ': ' + str(run) + '"\n',
              "********************************************")
        p = Popen([python_exe,
                   BetaBeatsrc_path + 'measure_optics.py',
                   '--model', model_path,
                   '--accel', 'skekb',
                   '--files', harmonic_output_path + run,
                   '--output', phase_output_path + run + '/'])
        p.wait()
        finish = time.time() - start
        timer(i, len(sdds_files), finish)
    return print(" ********************************************\n",
                 "phase analysis:\n",
                 '"Phase analysis finished."\n',
                 "********************************************")


def asynch_analysis(python_exe, phase_output_path, main_output_path):
    """
    Function to call async.py script to check phase output for
    unsynched BPMs.
    """
    for axis in ['x', 'y']:
        p = Popen([python_exe,
                   'async.py',
                   '--phase_output_dir', phase_output_path,
                   '--async_output_dir', main_output_path + 'outofphase' + axis + '/',
                   '--axis', axis])
        p.wait()
    return print(" ********************************************\n",
                 "asynch_analysis:\n",
                 '"Asynchronous BPMs found."\n',
                 "********************************************")


def asynch_schem(python_exe, sdds_path, main_output_path, when='before'):
    """
    Function to call checkBPMs_schematic.py script to see correction
    script's response to asynched BPMs.
    """
    for axis in ['x', 'y']:
        p = Popen([python_exe,
                   'checkBPMs_schematic.py',
                   '--axis', axis,
                   '--sdds_dir', sdds_path,
                   '--async_output_dir', main_output_path + 'outofphase' + axis + '/',
                   '--when', when,
                   '--save'])
        p.wait()
    return print(" ********************************************\n",
                 "asynch_schem:\n",
                 '"BPM synchronisation schematic saved in main output directory."\n',
                 "********************************************")


def asynch_cmap(python_exe, sdds_path, phase_output_path, when='before'):
    """
    Function to call checkBPMs_colourmap.py script to see actual
    phase difference between BPMs.
    """
    for axis in ['x', 'y']:
        p = Popen([python_exe,
                   'checkBPMs_colormap.py',
                   '--axis', axis,
                   '--sdds_dir', sdds_path,
                   '--phase_output_dir', phase_output_path,
                   '--when', when,
                   '--save'])
        p.wait()
    return print(" ********************************************\n",
                 "asynch_cmap:\n",
                 '"BPM synchronisation colormap saved in main output directory."\n',
                 "********************************************")


# ====================================================
# To be used in async.py
# ====================================================
def phase(datapath, axis):
    """
    Reads getphase*.out and returns required columns as arrays.
    """
    with open(datapath + 'getphase' + axis + '.out') as f:
        lines=f.readlines()
    S1 = [float(lines[10+i].split()[0]) for i in range(len(lines[10:]))]
    S2 = [float(lines[10+i].split()[4]) for i in range(len(lines[10:]))]
    Sall = np.hstack([S1, S2[-1]])
    name1 = [lines[10+i].split()[2] for i in range(len(lines[10:]))]
    name2 = [lines[10+i].split()[3] for i in range(len(lines[10:]))]
    namesall = np.hstack([name1, name2[-1]])
    deltaph = [float(lines[10+i].split()[-1]) for i in range(len(lines[10:]))]
    phx = [float(lines[10+i].split()[-2]) for i in range(len(lines[10:]))]
    phxmdl = [float(lines[10+i].split()[-4]) for i in range(len(lines[10:]))]
    Qx = float(lines[5].split()[3])
    Qy = float(lines[6].split()[3])
    return Sall, namesall, deltaph, phx, phxmdl, Qx, Qy


def phasetot(datapath, axis):
    """
    Reads getphasetot*.out and returns deltaphtot array.
    """
    with open(datapath + 'getphasetot' + axis + '.out') as f:
        lines = f.readlines()[8:]
    deltaphtot = [float(lines[2+i].split()[-1]) for i in range(len(lines[2:]))]
    return deltaphtot


# ====================================================
# To be used in checkBPMs*.py
# ====================================================
def BPMs_from_sdds(sddsfile):
    """
    Finds the complete list of BPMs from the sdds file.
    """
    with open(sddsfile) as f:
        lines = f.readlines()
    lines = [line for line in lines if not line.startswith('#')]

    BPMs = []
    badBPMs = []
    for line in lines:
        if line.startswith('0'):
            BPMs.append(line.split()[1])
            if line.split()[3] == '.0000000000':
                badBPMs.append(line.split()[1])

    return BPMs, badBPMs


def get_all_outofsynch(async_output_dir):
    """
    Creates a dictionary with keys corresponding to the
    <run>.txt filename of the measurement run, as
    given in file_dict.txt, and each entry containing
    the list of BPMs along with their integer
    out-of-synch values, as stated in the respective
    outofsynch/<file>.txt file.
    """
    files = os.listdir(async_output_dir)
    all_outofsynch = {}
    for i, fn in enumerate(files):
        with open(async_output_dir + fn) as f:
            column = f.readlines()
        del column[-1]
        del column[0]
        all_outofsynch[files[i]] = column
    return all_outofsynch


def get_dict_schematic(dictionary, file):
    """
    For the file with name <file>, returns a dictionary
    of keys corresponding to each BPM in that file, and
    key entries consisting of the status of that BPM as
    a string:
    '+1', '0' or '-1'.
    """
    def get_info(pattern):
        info = []
        for key_entry in dictionary[file]:
            info.append(re.search(pattern, key_entry).group(1))
        return info
    names = get_info('\"([A-Z0-9]+)\"\S*')
    asynchs = get_info('\-\>([\+\-]*[0-9])')
    Dict = {}
    for i in range(len(names)):
        Dict[names[i]] = asynchs[i]
    return Dict


def get_dict_colormap(names, phases):
    """
    Given an array of BPM names and their respective
    phases, returns a dictionary with BPM name keys
    and phase advance entries.
    """
    Dict = {}
    for i in range(len(names)):
        Dict[names[i]] = phases[i]
    return Dict


def get_data_column(phase_output_dir, folder, data, column):
    """
    Obtain desired data column from measurement run in phase
    output dir as an array.
    """
    with open(phase_output_dir + folder + '/' + data) as f:
        lines = f.readlines()
    rows = [line for line in lines if line.split()[0] not in ['@', '*', '$']]
    headers, = [line for line in lines if line.split()[0] == '*']
    headers = headers.split()[1:]
    all_dat = {}
    for i in range(len(headers)):
        if headers[i] in ['NAME', 'NAME2']:
            all_dat[headers[i]] = [rows[j].split()[i] for j in range(len(rows))]
        else:
            all_dat[headers[i]] = [float(rows[j].split()[i]) for j in range(len(rows))]
    return all_dat[column]


# ====================================================
# To be used in run_BetaBeatsrc.py
# ====================================================

def timer(i_current, i_total, time_i):
    """
    Estimates how long until analysis complete.
    """
    total_time = time_i * (i_total-1)
    time_remaining = total_time - i_current*time_i
    minutes = int(time_remaining//60)
    seconds = int(round(time_remaining - minutes*60))
    return print(" #####################################################\n",
                 "TIMER TIMER TIMER TIMER TIMER TIMER TIMER TIMER TIMER\n",
                 "\n",
                 "Approximate time remaining: ", str(minutes), "m" + str(seconds) + "s\n",
                 "\n",
                 "TIMER TIMER TIMER TIMER TIMER TIMER TIMER TIMER TIMER\n",
                 "#####################################################\n")
    #sys.stdout.write('\r')
    #sys.stdout.write("TIMER TIMER TIMER TIMER TIMER TIMER TIMER TIMER TIMER\n" +
    #                 "\n" +
    #                 "Approximate time remaining: " + str(minutes) + "m" + str(seconds) + "s\n" +
    #                 "\n" +
    #                 "TIMER TIMER TIMER TIMER TIMER TIMER TIMER TIMER TIMER\n")
    #sys.stdout.flush()
    #return

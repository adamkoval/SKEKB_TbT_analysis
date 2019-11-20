"""
File containing functions for all python scripts in this package.
"""
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
        if file.endswith('.data') and file.startswith(ringID.upper()):
            files.append(file)
    
    fd = open(file_dict, 'w')
    fd.write('{\n')
    for i, file in enumerate(files):
        before = os.path.join(input_data_dir, file)
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
        if debug is True:
            loopend = '2'
        else:
            loopend = 'Length[runs]'
        if asynch_info == False:
            fn = 'prerun.sad'
        else:
            fn = 'run.sad'
        LINE = get_LINE(lattice, gsad)
        file = open(fn, "w")
        file.write(#'FFS;\n'
                #    'GetMAIN["' + lattice + '"];\n'
                   'read "' + lattice + '" ;\n'
                   '\n'
                   'FFS USE ' + LINE + ';\n'
                   'CELL; CALC;\n'
                   'emit;\n'
                #    'em=Emittance[];\n'    
                   'Get["func.n"];\n\n'
                   'runs = Get["' + file_dict + '"];\n'
                   'Do[\n'
                   '    fnr1 = "./"//runs[i, 1];\n')
        if asynch_info == False:
            file.write('    fbpm = "None";\n')
        elif asynch_info == True:
            file.write('    fbpm = "' + main_output_dir + 'outofphase' + kickax.lower() + '/"//runs[i, 2]//".txt";\n')
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
            user_input = input('There is no dictionary file present for .data -> .sdds conversion. Would you like to create a new one (input -> create (\'create\' in python 2)) or would you like to provide one (input -> provide (\'provide\' in pyhton 2))?\n')
            if user_input == 'create':
                generic_dict(input_data_dir, file_dict, ringID)
                continue
            elif user_input == 'provide':
                continue
    if os.path.exists(sdds_dir):
        # Checking if it is empty
        if os.listdir(sdds_dir):
            while True:
                user_input = input(sdds_dir + ' directory contains files. Would you like to clean the directory and start from scratch? (options: yes, no, show contents (python 3) or \'yes\', \'no\', \'show contents\' (python 2)\n')
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
    for line in lines: #[9830:9835]
        if line.split()[0] == 'LINE':
            RINGNAME = line.split()[1]
            return RINGNAME


def makemodel_and_guesstune(model_path, lattice, gsad):
    """
    Function which creates a model for BetaBeat.src analysis and
    generates and executes SAD script to obtain initial guesses
    for x & y tunes.
    """
    LINE = get_LINE(lattice, gsad)
    if not os.path.exists(model_path):
        os.system('mkdir ' + model_path)
    else:
        pass

    if len(os.listdir(model_path)) > 2:
        print('\nThe following files have been found in the model directory:')
        print(os.listdir(model_path),'\n')
        while True:
            user_input = input('Do you wish to proceed with the model creation? (y/n):')
            if user_input == 'y':
                break
            elif user_input == 'n':
                print('No model is created.')
                return
            else:
                print('Please enter a valid input ("y" or "n").')
                continue
        
    fn = 'model_and_tune.sad'
    file = open(fn, "w")
    file.write(#'FFS;\n\n'
            #    'GetMAIN["' + lattice + '"];\n'
               'read "' + lattice + '" ;\n'
               'FFS USE ' + LINE + ';\n'
               'CELL;\n'
               'CALC;\n'
            #    'emit;\n\n'
               'em = Emittance[];\n\n'
               'Get["func.n"];\n\n'
               'fn1 = "' + model_path + '/twiss.dat";\n'
               'fn2 = "' + model_path + '/twiss_elements.dat";\n'
               'SaveTwiss[fn1, fn2];\n\n'
               'file = OpenWrite["tune_guess.txt"];\n'
               'WriteString[file, "Qx = ", Twiss["nx", $$$]/(2*Pi), "\\n"];\n'
               'WriteString[file, "Qy = ", Twiss["ny", $$$]/(2*Pi), "\\n"];\n'
               'Close[file];\n'
               '\n'
               'abort;\n')
    file.close()
    os.system(gsad + ' ' + fn)

    # create several twiss files to then compute second order dispersion in plotting script 
    for dp0 in np.arange(-1e-3, 1.1e-3, 1e-4):
        # print(round(dp0,4))
        fn = 'offmom_model.sad'
        ff = open(fn,'w')
        ff.write(#'FFS;\n\n'
                # 'GetMAIN["' + lattice + '"];\n'
                'read "' + lattice + '" ;\n'
                'FFS USE ' + LINE + ';\n'
                'CELL;\n'
                'DP0='+str(round(dp0,4))+';\n'
                'CALC;\n'
                'em = Emittance[];\n\n'
                'Get["func.n"];\n\n'
                'fn1 = "' + model_path + '/twiss_dp0_'+str(round(dp0,4))+'.dat";\n'
                'fn2 = "' + model_path + '/twiss_elements_dp0_'+str(round(dp0,4))+'.dat";\n'
                'SaveTwiss[fn1, fn2];\n\n'
                'abort;\n')
        ff.close()
        os.system(gsad + ' ' + fn)

    return print(" ********************************************\n",
                 "makemodel_and_guesstunes:\n",
                 '"' + fn + ' finished, model is ready in ' + model_path + ' and tune guesses are written to tune_guess.txt."\n',
                 "********************************************")


def harmonic_analysis(py_version, python_exe, BetaBeatsrc_path, model_path,
                      harmonic_output_path, sdds_path, nturns,
                      tune_range, lattice, gsad):
    """
    Function to call hole_in_one.py script from BetaBeat.src or omc3.
    """
    makemodel_and_guesstune(model_path, lattice, gsad)
    with open('tune_guess.txt') as f:
        lines = f.readlines()
    model_tunex = lines[0].split()[2]
    model_tuney = lines[1].split()[2]
    model_tunex = '0.' + re.match('[0-9]+\.([0-9]+)', model_tunex).group(1)
    model_tuney = '0.' + re.match('[0-9]+\.([0-9]+)', model_tuney).group(1)
    drv_tunex = model_tunex
    drv_tuney = model_tuney
    max_peak = '5.0'
    tunez = '0'
    if not os.path.exists(harmonic_output_path):
        os.system('mkdir ' + harmonic_output_path) 

    sdds_files = [ff for ff in os.listdir(sdds_path) if '.sdds' in ff ]

    for i, run in enumerate(sdds_files):
        start = time.time()
        print(" ********************************************\n",
              "harmonic analysis:\n",
              '"Working on file ' + str(i+1) + '/' + str(len(sdds_files)) + ': ' + str(run) + '"\n',
              "********************************************")
        if py_version > 2:
            os.system(str(python_exe) +' '
                    +str(BetaBeatsrc_path) + 'hole_in_one.py'
                    ' --harpy'
                    ' --files ' + os.path.join(sdds_path, run) +
                    ' --outputdir ' + harmonic_output_path + 
                    ' --model '+ model_path + 'twiss.dat'
                    ' --tunes '+ drv_tunex + ' ' + drv_tuney + ' ' + tunez +
                    ' --nattunes ' + model_tunex + ' ' + model_tuney + ' ' + tunez+
                    ' --turns ' + tunez + ' ' + nturns +
                    ' --tolerance ' + tune_range +
                    ' --unit mm' # ("m", "cm", "mm", "um")
                    ' --keep_exact_zeros'
                    ' --to_write spectra bpm_summary lin'
                    ' --clean'
                    ' --max_peak ' + max_peak +
                    ' --tune_clean_limit 1e-4')        
        else:
            p = Popen([python_exe,
                    BetaBeatsrc_path + 'hole_in_one.py',
                    '--file', os.path.join(sdds_path, run),
                    '--outputdir', harmonic_output_path,
                    '--model', model_path + 'twiss.dat',
                    '--startturn', '2',
                    '--endturn', nturns,
                    'harpy',
                    '--harpy_mode', 'bpm',
                    '--tunex=' + drv_tunex,
                    '--tuney=' + drv_tuney,
                    '--nattunex=' + model_tunex,
                    '--nattuney=' + model_tuney,
                    '--tolerance=' + tune_range,
                    '--tune_clean_limit=1e-4']) # changed from 1e-5 to 10e-5 so that fewer BPMs are cleaned
            p.wait()
        finish = time.time() - start
        timer('Harmonic analysis', i, len(sdds_files), finish)
    return print(" ********************************************\n",
                 "harmonic analysis:\n",
                 '"Harmonic analysis finished."\n',
                 "********************************************")


def group_runs(files):
    """
    Groups repeated measurements at the same setting for use in phase_analysis().
    Files must be named name_xx.sddds where x can be any character, hence up to 99 files
    can be summarised within one group. 
    """
    # all_groups = {}
    # oldsetting = re.match('(\S*)\_[0-9]+\.sdds', files[0]).group(1)
    # group = [files[0]]
    # for file in files[1:]:
    #     setting = re.match('(\S*)\_[0-9]+\.sdds', file).group(1)
    #     if setting == oldsetting:
    #         group.append(file)
    #         oldsetting = setting
    #         if file == files[-1]:
    #             all_groups[oldsetting] = group
    #         else:
    #             pass
    #     else:
    #         all_groups[oldsetting] = group
    #         group = [file]
    #         oldsetting = setting
    # print(all_groups)

    all_groups = {}
    files_reduced = [ff[:-7] for ff in files] 
    groups = list(set(files_reduced))
    for i, group in enumerate(groups):
        indices = [i for i, s in enumerate(files_reduced) if str(group) in s]
        grouped_files = []
        for ind in indices:
            grouped_files.append(files[ind])
        all_groups[group] = grouped_files
        
    return all_groups


def phase_analysis(py_version, python_exe, BetaBeatsrc_path, model_path,
                   harmonic_output_path, phase_output_path, sdds_path, 
                   ringID, group_flag, all_at_once_flag):
    """
    Function to call measure_optics.py script from BetaBeat.src or omc3.
    """
    if not os.path.exists(phase_output_path):
        os.system('mkdir ' + phase_output_path)
    sdds_files = [ff for ff in os.listdir(sdds_path) if '.sdds' in ff ]
    
    if (group_flag or all_at_once_flag) is not True:
        for i, run in enumerate(sdds_files):
            start = time.time()
            print(" ********************************************\n",
                "phase analysis:\n",
                '"Working on file ' + str(i+1) + '/' + str(len(sdds_files)) + ': ' + str(run) + '"\n',
                "********************************************")
            if py_version > 2:
                p = Popen([python_exe,
                        BetaBeatsrc_path + 'hole_in_one.py',
                        '--optics',
                        '--files', os.path.join(harmonic_output_path, run),
                        '--outputdir', os.path.join(phase_output_path, run),
                        '--model_dir', model_path,
                        '--accel', 'skekb',
                        '--ring', ringID,
                        '--compensation','none'])
            else:
                p = Popen([python_exe,
                        BetaBeatsrc_path + 'GetLLM/GetLLM.py',
                        '--model', model_path + '/twiss.dat',
                        '--accel', 'skekb',
                        '--files', os.path.join(harmonic_output_path, run),
                        '-b','m',
                        '--coupling', '0',
                        '--output', os.path.join(phase_output_path, run)])      
                # DO NOT USE MEASURE OPTICS IN PYTHON 2 UNLESS YOU WANT TO CHECK SOMETHING
                # p = Popen([python_exe,
                #         BetaBeatsrc_path + 'measure_optics.py',
                #         '--model', model_path,
                #         '--accel', 'skekb',
                #         '--files', harmonic_output_path + run,
                #         '--output', phase_output_path + run + '/'])
            p.wait()
            finish = time.time() - start
            timer('Phase analysis [single]', i, len(sdds_files), finish)
    
    if group_flag == True:
        grouped_files = group_runs(sdds_files)
        for i, group in enumerate(grouped_files):
            if py_version > 2:
                group_s = str()
                for j in grouped_files[group]:
                    group_s +=' '+str(os.path.join(harmonic_output_path, j)) 
            else:
                group_s = ','.join([harmonic_output_path+j for j in grouped_files[group]])
            start = time.time()
            
            print(" ********************************************\n",
                  "phase analysis:\n",
                  '"Working on group '+str(i+1)+'/'+str(len(grouped_files))+ ': ' +str(group)+'"\n',
                  "********************************************")
            if py_version > 2:
                os.system(str(python_exe)+' '
                        +str(BetaBeatsrc_path)+'hole_in_one.py'
                        ' --optics'
                        ' --accel skekb'
                        ' --ring '+str(ringID)+
                        ' --compensation none'
                        ' --second_order_dispersion'
                        #' --union'
                        ' --model_dir '+str(model_path)+
                        ' --outputdir '+str(os.path.join(phase_output_path, str(group)))+
                        ' --files '+str(group_s))
            else:
                p = Popen([python_exe,
                        BetaBeatsrc_path + 'GetLLM/GetLLM.py',
                        '--model', model_path + '/twiss.dat',
                        '--accel', 'skekb',
                        '--files', str(group_s),
                        # '-k 10000',
                        # '-e 10000',
                        '-b', 'm',
                        '--coupling', '0',
                        '--output', os.path.join(phase_output_path, str(group))]) 
                # DO NOT USE MEASURE OPTICS IN PYTHON 2 UNLESS YOU WANT TO CHECK SOMETHING
                # p = Popen([python_exe,
                #         BetaBeatsrc_path + 'measure_optics.py',
                #         '--model', model_path,
                #         '--accel', 'skekb',
                #         '--files', str(group_s),
                #         '--output', str(os.path.join(phase_output_path, str(group)))])
                p.wait()
            finish = time.time() - start
            timer('Phase analysis [average]', i, len(sdds_files), finish)
    
    if all_at_once_flag == True:
        print(" ********************************************\n",
                "phase analysis:\n",
                '"Working on all-at-once analysis for e.g. dispersion."\n',
                "********************************************")
        allff = str()
        if py_version > 2:
            for ff in sdds_files:
                allff = allff + os.path.join(harmonic_output_path,ff) + ' '
        else:
            for ff in sdds_files:
                allff = allff + os.path.join(harmonic_output_path,ff) + ','
        allff = allff[:-1]
        if py_version > 2:
            os.system(str(python_exe)+' '
                    +str(BetaBeatsrc_path)+'hole_in_one.py'
                    ' --optics'
                    ' --accel skekb'
                    ' --ring '+str(ringID)+
                    ' --compensation none'
                    ' --second_order_dispersion'
                    #' --union'
                    ' --model_dir '+str(model_path)+
                    ' --outputdir '+str(os.path.join(phase_output_path, 'average/' ))+
                    ' --files '+str(allff))
        else:
            p = Popen([python_exe,
                        BetaBeatsrc_path + 'GetLLM/GetLLM.py',
                        '--model', model_path + '/twiss.dat',
                        '--accel', 'skekb',
                        '--files', str(allff),
                        '-k 10000',
                        '-e 10000',
                        '-b', 'm',
                        '--coupling', '0',
                        '--output', os.path.join(phase_output_path, 'average/')])    
            p.wait()
        
    return print(" ********************************************\n",
                 "phase analysis:\n",
                 '"Phase analysis finished."\n',
                 "********************************************")


def asynch_analysis(python_exe, phase_output_path, main_output_path, model_path, ringID):
    """
    Function to call async.py script to check phase output for
    unsynched BPMs.
    """
    sdds_dir = os.path.join(main_output_path, 'unsynched_sdds')
    sdds = os.path.join(sdds_dir, os.listdir(sdds_dir)[1])

    for axis in ['x', 'y']:
        os.system(str(python_exe)+
                   ' async.py'
                   ' --phase_output_dir '+ phase_output_path +
                   ' --async_output_dir '+ main_output_path + 'outofphase' + axis + '/'+
                   ' --sdds ' + str(sdds) +
                   ' --axis '+ axis +
                   ' --ring '+ ringID)
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
        for form in ['png', 'pdf']:
            p = Popen([python_exe,
                    'checkBPMs_colormap.py',
                    '--axis', axis,
                    '--sdds_dir', sdds_path,
                    '--phase_output_dir', phase_output_path,
                    '--when', when,
                    '--form', form,
                    '--save'])
            p.wait()
    return print(" ********************************************\n",
                 "asynch_cmap:\n",
                 '"BPM synchronisation colormap saved in main output directory."\n',
                 "********************************************")


def bpm_calibration(python_exe, synched_sdds, synched_harmonic_output, synched_phase_output,
                    calibrated_harmonic_output, calibrated_phase_output, ringID):
    """
    Function to call calibration.py script to calibrate amplitudes.
    Warning: ONLY tested using python 3 !
    """
    for plane in ['x','y']:
        os.system(python_exe + ' calibration.py'
                    ' --sdds ' + synched_sdds +
                    ' --plane ' + plane +
                    ' --ring ' + ringID )


def calib_hist(python_exe, synched_sdds, phase_output, when='before'):
    """
    Function to call checkCALIBRATION_histogram.py to make histogram of
    (beta_amp - beta_phase)/beta_phase  beating.
    """
    for plane in ['x', 'y']:
        for form in ['png', 'pdf']:
            os.system(python_exe + ' checkCALIBRATION_histogram.py' +
                        ' --sdds ' + synched_sdds +
                        ' --phase ' + phase_output +
                        ' --axis ' + plane + 
                        ' --when ' + when +
                        ' --pngpdf ' + form )


def freq_spec(python_exe, sdds, model):
    """
    Function to call checkFrequency.py to make plot of frequency spectrum.
    """
    for plane in ['x', 'y']:
        for form in ['png', 'pdf']:
            os.system(python_exe + ' checkFrequency.py' +
                        ' --sdds ' + sdds +
                        ' --model ' + model +
                        ' --axis ' + plane + 
                        ' --pngpdf ' + form )


def chromatic_analysis(model_path, phase_output):
    """
    Computes chromaticity and writes them to an output file.
    WARNING: ONLY TESTED FOR PYTHON 3!
    """
    for plane in ['x', 'y']:
        for pngpdf in ['png', 'pdf']:
            fo2 = os.path.join(phase_output, 'average/getkick.out')
            fo3 = os.path.join(phase_output, 'average/kick_' + plane + '.tfs')
            if os.path.isfile(fo3): ff = fo3
            else: ff = fo2

            with open(ff) as fo:
                lines = fo.readlines()
            fo.close()
            dpp_meas = np.array([float(lines[11+i].split()[1]) for i in range(len(lines[11:]))])

            Q = np.array([float(lines[11+i].split()[3]) for i in range(len(lines[11:]))])
            Q_err = [float(lines[11+i].split()[4]) for i in range(len(lines[11:]))]
            
            fit, cov = np.polyfit(dpp_meas, Q, 3, cov=True)
            poly = np.poly1d(fit)
            chrom1 = np.polyder(poly)
            chrom2 = np.polyder(chrom1)
            chrom3 = np.polyder(chrom2)

            chromaticity = os.path.join(phase_output, 'average/chromaticity_'+plane+'.tfs')
            chrom = open(chromaticity, 'w')
            chrom.write("@ Q"+plane+' '+str(poly(0.0))+' +/- '+str(np.sqrt(cov[3][3]))+'\n')
            chrom.write("@ Q'"+plane+' '+str(chrom1(0.0))+' +/- '+str(np.sqrt(cov[2][2]))+'\n')
            chrom.write("@ Q''"+plane+' '+str(chrom2(0.0))+' +/- '+str(2*np.sqrt(cov[1][1]))+'\n')
            chrom.write("@ Q'''"+plane+' '+str(chrom3(0.0))+' +/- '+str(6*np.sqrt(cov[0][0]))+'\n\n')

            try:
                model = os.path.join(model_path, 'tune_over_mom.txt')
                with open(model) as mo:
                    lines = mo.readlines()
                mo.close()

                col = 1 if plane == 'x' else 2
                Q_mdl = np.array([float(lines[1+i].split()[col]) for i in range(len(lines[1:]))])
                dpp_mdl = np.array([float(lines[1+i].split()[0]) for i in range(len(lines[1:]))])
                Q_mdl = np.array([Q_mdl[i] for i in range(len(Q_mdl)) if abs(dpp_mdl[i])<0.0025])
                dpp_mdl = np.array([dpp_mdl[i] for i in range(len(dpp_mdl)) if abs(dpp_mdl[i])<0.0025])
                
                fit_mdl, cov_mdl = np.polyfit(dpp_mdl, Q_mdl, 3, cov=True)
                poly_mdl = np.poly1d(fit_mdl)
                chrom1_mdl = np.polyder(poly_mdl)
                chrom2_mdl = np.polyder(chrom1_mdl)
                chrom3_mdl = np.polyder(chrom2_mdl)
            
                chrom.write("@ MDL Q"+plane+' '+str(poly_mdl(0.0))+' +/- '+str(np.sqrt(cov_mdl[3][3]))+'\n')
                chrom.write("@ MDL Q'"+plane+' '+str(chrom1_mdl(0.0))+' +/- '+str(np.sqrt(cov_mdl[2][2]))+'\n')
                chrom.write("@ MDL Q''"+plane+' '+str(chrom2_mdl(0.0))+' +/- '+str(2*np.sqrt(cov_mdl[1][1]))+'\n')
                chrom.write("@ MDL Q'''"+plane+' '+str(chrom3_mdl(0.0))+' +/- '+str(6*np.sqrt(cov_mdl[0][0]))+'\n')
            
            except:
                print(" ********************************************\n",
                    "Chromatic analysis:\n",
                    '"No accurate model found."\n',
                    "********************************************")
            
            chrom.close()
            
            dpp = np.arange(1.1*min((dpp_meas)),1.1*max((dpp_meas)),1e-4)

            try:
                size=20
                num=1
                import matplotlib.pyplot as plt
                plt.figure(figsize=(10,4.5))
                plt.plot(dpp, poly_mdl(dpp)-poly_mdl(0.0), label = 'Model', c='#1f77b4')
                plt.plot(dpp, poly(dpp)-poly(0.0), label = 'Fit', c='#ff7f0e')
                #plt.errorbar(dpp_meas, Q, yerr=Q_err, fmt = 'o', ms=5.5, mec= '#d62728', mfc = 'None', capsize=4, c = '#d62728', label = 'Measurement')
                plt.errorbar(dpp_meas, Q-poly(0.0), yerr=Q_err, fmt = 'o', ms=5.5, mec= '#d62728', mfc = 'None', capsize=4, c = '#d62728', label = 'Measurement')
                plt.legend(loc = 9, ncol = 3, fontsize=size, bbox_to_anchor=(0.5, 1.42), fancybox=True,  numpoints=1, scatterpoints = 1)
                plt.tick_params('both', labelsize=size)
                plt.xlabel(r'$\delta_{p}$', fontsize=size)
                if plane == 'x': plt.ylabel(r'$\Delta Q_{x}$', fontsize=size)
                else: plt.ylabel(r'$\Delta Q_{y}$', fontsize=size)
                plt.xlim(1.1*min((dpp_meas)),1.1*max((dpp_meas)))
                plt.tight_layout()
                plt.savefig(phase_output+'/average/Chroma_w_MDL_'+plane+'.'+pngpdf, bbox_inches='tight')
                plt.close(num)
                num=num+1
            except:
                print(" ********************************************\n",
                    "Chromatic analysis:\n",
                    '"I could not plot model chromaticity."\n',
                    "********************************************")
            
            try:
                plt.figure(figsize=(10,4.5))
                plt.plot(dpp, poly(dpp)-poly(0.0), label = 'Fit', c='#ff7f0e')
                plt.errorbar(dpp_meas, Q-poly(0.0), yerr=Q_err, fmt = 'o', ms=5.5, mec= '#d62728', mfc = 'None', capsize=4, c = '#d62728', label = 'Measurement')
                plt.legend(loc = 9, ncol = 3, fontsize=size, bbox_to_anchor=(0.5, 1.42), fancybox=True,  numpoints=1, scatterpoints = 1)
                plt.tick_params('both', labelsize=size)
                plt.xlabel(r'$\delta_{p}$', fontsize=size)
                if plane == 'x': plt.ylabel(r'$\Delta Q_{x}$', fontsize=size)
                else: plt.ylabel(r'$\Delta Q_{y}$', fontsize=size)
                plt.xlim(1.1*min((dpp_meas)),1.1*max((dpp_meas)))
                plt.tight_layout()
                plt.savefig(phase_output+'/average/Chroma_'+plane+'.'+pngpdf, bbox_inches='tight')
                plt.close(num)
            except:
                print(" ********************************************\n",
                    "Chromatic analysis:\n",
                    '"I could not plot chromaticity."\n',
                    "********************************************")



def coupling_analysis(model_path, synched_sdds, synched_harmonic_output, synched_phase_output, all_at_once_flag):
    """
    Computes f1010 and writes them to an output file.
    WARNING: ONLY TESTED FOR PYTHON 3!
    """
    all_bpms = read_bpms(os.path.join(synched_sdds, os.listdir(synched_sdds)[0]))

    if all_at_once_flag is not True:
        for sdds in os.listdir(synched_sdds):                        
            linx = os.path.join(synched_harmonic_output, sdds+'.linx')
            liny = os.path.join(synched_harmonic_output, sdds+'.liny')

            with open(linx) as fx: linesx=fx.readlines()[7:]
            fx.close()
            with open(liny) as fy: linesy=fy.readlines()[7:]
            fy.close()

            bpmx = [linesx[i].split()[0] for i in range(len(linesx)) ]
            AMP_01H =  ([float(linesx[i].split()[20]) for i in range(len(linesx)) ])
            ERRAMP_01H =  ([float(linesx[i].split()[-9]) for i in range(len(linesx)) ])
            
            bpmy = [linesy[i].split()[0] for i in range(len(linesy)) ]
            AMP_10V =  ([float(linesy[i].split()[20]) for i in range(len(linesy)) ])
            ERRAMP_10V =  ([float(linesy[i].split()[-9]) for i in range(len(linesy)) ])

            false_bpm = []
            
            for i, b in enumerate(all_bpms):    
                if b not in bpmx: 
                    AMP_01H.insert(i, 1)
                    ERRAMP_01H.insert(i, 1)
                    false_bpm.append(b)
                if b not in bpmy:
                    AMP_10V.insert(i, 1)
                    ERRAMP_10V.insert(i, 1)
                    false_bpm.append(b)
            print(false_bpm)
            AMP_01H = np.array(AMP_01H)
            ERRAMP_01H = np.array(ERRAMP_01H)
            AMP_10V = np.array(AMP_10V)
            ERRAMP_10V = np.array(ERRAMP_10V)
            
            av_f1010 = 0.5*((AMP_01H*AMP_10V)**0.5)
            err_av_f1010 = ( (ERRAMP_01H*AMP_10V)**2 / (16*(AMP_01H*AMP_10V)) + (ERRAMP_10V*AMP_01H)**2 /(16*(AMP_01H*AMP_10V)))**0.5
                        
            f1010_ff = os.path.join(synched_phase_output, sdds+'/f1010.tfs')
            f1010 = open(f1010_ff, 'w')
            f1010.write('*BPM\t\t\t\t|F1010|\t\t\t\t\t\tERR|F1010|\n')
            f1010.write('$ %s \t\t\t\t %f \t\t\t\t\t\t %f \n')
            for i, bpm in enumerate(all_bpms):
                if bpm in false_bpm:
                    f1010.write(all_bpms[i] + '\t\t\t' + str(0.0)+'\t\t\t'+ str(0.0)+'\n')
                else:
                    f1010.write(all_bpms[i] + '\t\t\t' + str(av_f1010[i])+'\t\t\t'+ str(err_av_f1010[i])+'\n')
            f1010.close()

    if all_at_once_flag == True:
        pass                    



def plot_optics(python_exe, phase_output, model, ringID):
    """
    Function to call script to plot all optics from OMC3 output.
    WARNING: only tested with python 3!
    """
    for axis in ['x', 'y']:
        for pngpdf in ['png', 'pdf']:
            os.system(python_exe + ' checkOptics.py ' +
                        ' --dir ' + phase_output +
                        ' --model ' + model + 
                        ' --axis ' + axis +
                        ' --ring ' + ringID +
                        ' --pngpdf ' + pngpdf )


# def damping_turns(python_exe, sdds):
#     """
#     Function to call checkExcitation.py to make plot of amplitude over turns.
#     """
#     for plane in ['x']:
#         for form in ['png']:
#             os.system(python_exe + ' checkExcitation.py' +
#                         ' --sdds ' + sdds +
#                         ' --axis ' + plane + 
#                         ' --pngpdf ' + form )


# ====================================================
# To be used in async.py and calibration.py
# ====================================================
def read_phase(datapath, axis):
    """
    Reads getphase*.out and returns required columns as arrays.
    """
    fo2 = os.path.join(datapath, 'getphase' + axis + '.out')
    fo3 = os.path.join(datapath, 'phase_' + axis + '.tfs')
   
    if os.path.isfile(fo3):
        ff = fo3
        with open(ff) as f:
            lines=f.readlines()
        S1 = [float(lines[10+i].split()[0]) for i in range(len(lines[10:]))]
        S2 = [float(lines[10+i].split()[3]) for i in range(len(lines[10:]))]
        Sall = np.hstack([S1, S2[-1]])
        name1 = [lines[10+i].split()[2] for i in range(len(lines[10:]))]
        name2 = [lines[10+i].split()[4] for i in range(len(lines[10:]))]
        namesall = np.hstack([name1, name2[-1]])
        deltaph = [float(lines[10+i].split()[-2]) for i in range(len(lines[10:]))]
        phx = [float(lines[10+i].split()[5]) for i in range(len(lines[10:]))]
        phxmdl = [float(lines[10+i].split()[7]) for i in range(len(lines[10:]))]
        Qx = float(lines[6].split()[3])
        Qy = float(lines[7].split()[3])

    elif os.path.isfile(fo2):
        ff = fo2
        with open(ff) as f:
            lines=f.readlines()
        S1 = [float(lines[11+i].split()[2]) for i in range(len(lines[11:]))]
        S2 = [float(lines[11+i].split()[3]) for i in range(len(lines[11:]))]
        Sall = np.hstack([S1, S2[-1]])
        name1 = [lines[11+i].split()[0] for i in range(len(lines[11:]))]
        name2 = [lines[11+i].split()[1] for i in range(len(lines[11:]))]
        namesall = np.hstack([name1, name2[-1]])
        phx = np.array([float(lines[11+i].split()[5]) for i in range(len(lines[11:]))])
        phxmdl = np.array([float(lines[11+i].split()[7]) for i in range(len(lines[11:]))])
        deltaph = phx- phxmdl
        Qx = float(lines[4].split()[3])
        Qy = float(lines[6].split()[3])

    
    else:
        return print(" ********************************************\n",
                 "asynch_cmap:\n",
                 '"No phase output files are found.. I stop now."\n',
                 "********************************************")
    
    return namesall, Qx, Qy
    # return Sall, namesall, deltaph, phx, phxmdl, Qx, Qy


def read_phasetot(datapath, axis):
    """
    Reads getphasetot*.out and returns deltaphtot array.
    """
    fo2 = os.path.join(datapath, 'getphasetot' + axis + '.out')
    fo3 = os.path.join(datapath, 'total_phase_' + axis + '.tfs')
    
    if os.path.isfile(fo3):
        ff = fo3
        with open(ff) as f:
            lines = f.readlines()[8:]
        deltaphtot = [float(lines[2+i].split()[-2]) for i in range(len(lines[2:]))]

    elif os.path.isfile(fo2):
        ff = fo2
        with open(ff) as f:
            lines = f.readlines()[11:]
        deltaphtot = [float(lines[2+i].split()[-1]) for i in range(len(lines[2:]))]

    else:
        return print(" ********************************************\n",
                 "asynch_cmap:\n",
                 '"No phase output files are found.. I stop now."\n',
                 "********************************************")

    return deltaphtot


def read_bpms(sdds):
    """
    Reads one sdds file and returns all BPM names as an array.
    """

    with open(sdds) as f:
        lines = f.readlines()
    f.close()
    bpm_lines = [lin for lin in lines if '0 M' in lin]
    names = [bpm_lines[i].split()[1] for i in range(len(bpm_lines))]

    return names


def read_bet_phase(folder, plane):
    """
    Reads beta_phase_*.tfs and returns the beta function.
    """
    file = os.path.join(folder, 'beta_phase_' + plane + '.tfs')
    with open(file) as fo:
        lines = fo.readlines()[15:]
    fo.close()
    beta_phase = [float(lines[i].split()[5]) for i in range(len(lines))]
    beta_phase_err = [float(lines[i].split()[6]) for i in range(len(lines))]
    bpms = [lines[i].split()[0] for i in range(len(lines))]
    return beta_phase, beta_phase_err, bpms


def read_bet_amp(folder, plane):
    """
    Reads beta_amplitude_*.tfs and returns the beta function.
    """
    file = os.path.join(folder, 'beta_amplitude_' + plane + '.tfs')
    with open(file) as fo:
        lines = fo.readlines()[12:]
    fo.close()
    beta_amp = [float(lines[i].split()[3]) for i in range(len(lines))]
    beta_amp_err = [float(lines[i].split()[4]) for i in range(len(lines))]
    return beta_amp, beta_amp_err


# def read_dx(folder, plane):
#     """
#     Reads dispersion_*.tfs and returns the disperison.
#     """
#     file = os.path.join(folder, 'dispersion_' + plane + '.tfs')
#     with open(file) as fo:
#         lines = fo.readlines()[10:]
#     fo.close()
#     dx = [float(lines[i].split()[9]) for i in range(len(lines))]
#     dx_err = [float(lines[i].split()[10]) for i in range(len(lines))]
#     bpms_dx = [float(lines[i].split()[0]) for i in range(len(lines))]
#     return dx, dx_err, bpms_dx


# def read_ndx(folder, plane):
#     """
#     Reads normalised_dispersion_*.tfs and returns the disperison.
#     """
#     file = os.path.join(folder, 'normalised_dispersion_' + plane + '.tfs')
#     with open(file) as fo:
#         lines = fo.readlines()[10:]
#     fo.close()
#     dx_n = [float(lines[i].split()[10]) for i in range(len(lines))]
#     dx_n_err = [float(lines[i].split()[11]) for i in range(len(lines))]
#     return dx_n, dx_n_err


def reject_outliers(data, m=2):
    """
    Removes outliers in a list.
    Outliers are farther than m*stddev away from mean. 
    """
    data = [val for val in data if (abs(val-np.mean(data)) < m*np.std(data))]
    return data


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
    # badBPMs = []
    for line in lines:
        if line.startswith('0'):
            BPMs.append(line.split()[1])
            # if line.split()[3] == '.0000000000':
            #     badBPMs.append(line.split()[1])

    return BPMs #, badBPMs


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

def timer(func_name, i_current, i_total, time_i):
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
                 "(", func_name, ")\n"
                 "Approximate time remaining: ", str(minutes), "m" + str(seconds) + "s\n",
                 "\n",
                 "TIMER TIMER TIMER TIMER TIMER TIMER TIMER TIMER TIMER\n",
                 "#####################################################\n")

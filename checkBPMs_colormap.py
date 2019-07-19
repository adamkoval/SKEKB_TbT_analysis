"""
Created on Tue Jun 11
Author: Adam Koval
"""
from __future__ import print_function
import os
import sys
import argparse
import pandas
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from func import BPMs_from_sdds, get_data_column, get_dict_colormap

# Argument parser
parser = argparse.ArgumentParser()
parser.add_argument('--axis', '-ax',
                    dest='axis',
                    action='store')
parser.add_argument('--phase_output_dir', '-pod',
                    dest='phase_output_dir',
                    action='store')
parser.add_argument('--sdds_dir', '-sd',
                    dest='sdds_dir',
                    action='store')
parser.add_argument('--display', '-d',
                    action='store_true')
parser.add_argument('--when',
                    choices=['before', 'after'])
parser.add_argument('--save', '-s',
                    action='store_true')
args = parser.parse_args()

# Definitions
axis = args.axis
AXIS = axis.capitalize()
sdds_dir = args.sdds_dir
phase_output_dir = args.phase_output_dir
data = 'getphasetot' + axis + '.out'

# List all files in phase_output_dir
file_list = os.listdir(phase_output_dir)

# List all BPMs from any sdds file
BPM_list = BPMs_from_sdds(sdds_dir + os.listdir(sdds_dir)[0])[0]

# Create dataframe for plotting
df = {}
for file in file_list:
    df[file] = []
    names = get_data_column(phase_output_dir, file, data, 'NAME')
    phases = get_data_column(phase_output_dir, file, data, 'DELTAPHASE' + AXIS)
    for BPM in BPM_list:
        try:
            df[file].append(get_dict_colormap(names, phases)[BPM])
        except KeyError:
            df[file].append(np.nan)
df = pandas.DataFrame(df, index=BPM_list)
df = df

# Set up the plot
with open('cmap.txt','r') as f:
    lines = f.readlines()
cmatrix = []
for i in range(len(lines)):
    cmatrix.append([float(j)/255.0 for j in lines[i].split()])
cm = colors.ListedColormap(cmatrix)

X, Y = np.meshgrid(
    np.linspace(
        0, len(BPM_list), len(BPM_list) + 1),
    np.linspace(
        0, len(file_list), len(file_list) + 1))
Z = df.T
fn = phase_output_dir + '../cmapdf_' + args.when + '.csv'
Z.to_csv(fn)
Z = pandas.read_csv(fn, index_col=0)

column_length = len(df.columns.tolist())
row_length = len(BPM_list)
y_posn = [i for i in range(column_length)]
x_posn = [i for i in range(row_length)]

# Plot
fig = plt.figure(figsize=(17, 11))
ax = fig.add_subplot(111)

plt.pcolormesh(X, Y, Z, cmap = cm)
bar = plt.colorbar()
bar.set_label('$\Delta\ \phi$ [2$\pi$]', fontsize=18)
bar.ax.tick_params(labelsize=18)

#for i in range(column_length):
#    if i%3 == 0 and i != 0:
#        ax.axhline(y_posn[i], ls='--', lw=1)

ax.set_xticks([i for i in range(row_length)])
ax.set_xticklabels(BPM_list, rotation='vertical')
#ax.set_yticks([i+.5 for i in y_posn])

yticklabels = []
all_meas = [i[:-4] for i in df.columns.tolist()]
yticklabels.append(all_meas[0][:-3])
for i in range(1, len(all_meas)):
    if all_meas[i-1][:-3] != all_meas[i][:-3]:
        yticklabels.append(all_meas[i][:-3])
ax.set_yticks([i for i in y_posn if (i+1)%5==0])
ax.set_yticklabels(yticklabels)
ax.set_xlabel('BPM', fontsize=18)
ax.set_ylabel('Measurement run', fontsize=18)
plt.title('SuperKEKB BPM performance from T-b-T data (' + axis + '-axis, ' + args.when  + ')', fontsize=22)

if args.save == True:
    plt.savefig(phase_output_dir + '../'
                + 'Asynchronous_BPMs_colourmap_'
                + axis + 'axis_' + args.when  +  '.png',
                format = 'png')
if args.display == True:
    plt.show()

print(" ********************************************\n",
      "checkBPMs_colormap.py:\n",
      '"Script made it to the end, moving on..."\n',
      "********************************************")

sys.exit()

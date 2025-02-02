# SKEKB\_TbT\_analysis
Package used for analysing Turn-by-Turn data from the SuperKEKB accelerator using tools developed by the CERN OMC team.


# I. Quick start guide
**Prerequisites**:

* Python2.7 with the following packges installed:
* OR: Python3.6 if analysis should be done with python3
    + numpy==1.15.0 (importnat! 1.16.x causes problems for Beta-Beat.src)
    + pandas==0.24.2
    + scipy==1.2.1
    + matplotlib==2.2.4
    + tkinter==8.6
    + NOTE: As the present package does not make use of Beta-Beat.src's graphical functions, it is possible to run it without prior installation of matplotlib and tkinter, see "matplotlib/Tkinter workaround" section.
* Beta-Beat.src package - https://github.com/pylhc/Beta-Beat.src.
* Strategic Accelerator Design (SAD) - https://github.com/KatsOide/SAD - see "SAD installation" section for install instructions.
* OMC3 package - https://github.com/pylhc/omc3

1) Edit the *pathnames.txt* file first, to ensure the package knows where to search for everything it needs. An example file, *pathnames_example.txt*, is supplied, which you can rename and edit any way you like. 
Things to keep in mind:
    * The program reads all the variables supplied (and ignores lines beginning with '#').
    * Everything is read in as a string, so one should not enclose values in parentheses.
    * Paths which define a directory must be ended with '/'. Perhaps in the future, a function to check for this can be added, but this doesn't exist at the moment. 

3) Run "python2 complete\_analysis.py --help" to see possible command line arguments.
    UPDATE: it is also possible to use python3, e.g. "python3 complete\_analysis.py"

4) Run again with desired command line arguments (see "Calling main script" section).

5) All output is directed into the directory defined in "main\_output\_path" variable in *pathnames.txt*.


# II. matplotlib/Tkinter workaround
- Comment out line 48 in the file *Beta-Beat.src/twiss\_optics/optics\_class.py*. The line reads "from plotshop import plot\_style as pstyle". 
- Please note, this will likely compromise other functions of the Beta-Beat.src package. Should the user wish to step outside of the scope of the present package, they should install matplotlib and tkinter, and other required packages.


# III. SAD installation 
# (Linux Debian)
1) Follow instructions on "https://github.com/KatsOide/SAD/blob/master/INSTALL", or follow below.
2) Clone repo and "cd" into it. 
3) Run "mv sad.conf.sample sad.conf".
4) Edit "sad.conf" -> set "SAD\_ROOT=/usr/local/SAD", set "USE\_X11=YES", set "USE\_TCLTK=USE\_X11".
5) If you don't have gfortran installed, run "sudo apt-get install gfortran".
6) Run "sudo make all".
# (Windows WSL)
1) Same as above, but I encountered the issue of not having the *yacc* compiler installed. If this is the case, run "sudo apt-get install bison", which includes yacc.


# IV. Get a lattice from KEK server
If no sad lattice is provided so far, it can be extracted from the KEK server using "extract_sadlattice.sad".
Note: This will only work if it runs at KEK server. 
To run SAD at KEK use the following command: "/SAD/bin/gs -env skekb" .
In addition, a SAD distribution by Oide-san can be used with: "/SAD/bin/gs -k64" . This has NOT been tested so use it on your own risk.


# V. Calling main script
The "complete_analysis.py" script takes mandatory and optional arguments.

Mandatory arguments are:
- **"- -pathnames":**
Path to *pathnames.txt* file, which contains all other paths necessary for the package.

Optional arguments are:
- **"- -harmonic1"/"-h1":**
Harmonic analysis without knowledge of BPM synch. This is enough to obtain tunes.
- **"- -phase1"/"-p1":**
Phase analysis of harmonic1 output without BPM synch knowledge.
- **"- -plotasynch1"/"-pa1":**
Plotting of BPM synchronisation from phase1 output, before synch fix is applied.
- **"- -asynch"/"-aa":**
Analysis of BPM synchronisation from phase1 output.
- **"- -harmonic2"/"-h2":**
sdds conversion and harmonic analysis with knowledge of BPM synch.
- **"- -phase2"/"-p2":**
Phase analysis of harmonic2 output with knowledge of BPM synch.
- **"- -plotoptics22"/"-po2":**
Plots the optics repository after BPM synchronisation.
- **"- -plotasynch2"/"-pa2":**
Plotting of BPM synchronisation from phase2 output, after synch fix is applied.
- **"- -calib"/"-c":**
Calculates the BPM calibration for this measurement.
- **"- -phase2"/"-p3":**
Phase analysis of harmonic3 output with knowledge of BPM calibration.
- **"- -plotcalib1"/"-pc1":**
Plotting of BPM calibration from phase2 output, before calibration is applied.
- **"- -plotcalib2"/"-pc2":**
Plotting of BPM calibration from phase3 output, after calibration is applied.
- **"- -group_runs"/"-g":**
To be used when multiple runs for a single setting are available.
- **"- -all_at_once"/"-all":**
To be used when all files should run at once, e.g. for dispersion measurement with off-momentum files.
- **"- -debug"/"-db":**
Debug option. Only does analysis on 2 files, as opposed to all.
- **"- -omc3"/"-o3":**
Using the OMC3 in python3 analysis package instead of Beta-Beat.src in python2.


Optional arguments may be applied all at once, or in separate calls of the "complete\_analysis.py" script in the order:

     -h1 <- -p1 <- -aa <- -h2 <- -p2 <- -c <- -p3,

where "a <- b" means that *b* depeds on *a*.  

Note also, that *-pa1* and *-pa2* may be used at will, but only once their respective phase analyses, *-p1* and *-p2*, have completed. Moreover, *-pc1* and *-pc2* may be used at will,
but only after the respective phase analyses, *-p2* and *-p3*, have been completed.

To illustrate the use of the command line arguments, one may call, in order:

    1) "python2 complete_analysis.py --pathnames pathnames.txt -h1 -p1"
    2) "python2 complete_analysis.py --pathnames pathnames.txt -aa"
    3) "python2 complete_analysis.py --pathnames pathnames.txt -h2"
    4) "python2 complete_analysis.py --pathnames pathnames.txt -pa1 -p2"

OR:

    1) "python2 complete_analysis.py --pathnames pathnames.txt -h1"
    2) "python2 complete_analysis.py --pathnames pathnames.txt -p1"
    3) "python2 complete_analysis.py --pathnames pathnames.txt -p2 -h2 -aa -pa2"

OR:

    1) "python2 complete_analysis.py --pathnames pathnames.txt -h1 -h2 -p2 -pa1 -pa2 -p1 -aa"

I.e., the order of arguments within a command line call doesn't matter, as long as all arguments dependent on each other are called together.


# V.I Caveats:

1) If the user doesn't supply any optional arguments, the only function which will be executed is the initial KEK TbT data file -> sdds conversion.

2) Keep in mind that *-pa1* & *-pa2* (also *-pc1* & *-pc2* ) utilise matplotlib and possibly also Tkinter, in case the workaround has been applied (see "matplotlib/Tkinter workaround").

3) The *-group* flag will not work properly if a custom "file_dict.txt" is not supplied. This is because the grouping function requires (*group_runs()* within func.py) that the sdds file names are suffixed with "_k.sdds", where *k* is an integer (starting from *1*) denoting a repeated measurement. For example, one could use the following naming convention in their custom "file_dict.txt":

		{
			{"input_data/EXAMPLE_2019_01_01_00_00_00.data", "NAME_1.sdds"},
			{"input_data/EXAMPLE_2019_01_01_00_00_01.data", "NAME_2.sdds"},
			{"input_data/EXAMPLE_2019_01_01_00_00_02.data", "NAME_3.sdds"}
		}
	Note: The grouping function searches the .sdds setting name using the regular expression *"(\S\*)\\_[0-9]+\\.sdds"*.

4) The *-all* flag will use all given lin files, independent of their name.
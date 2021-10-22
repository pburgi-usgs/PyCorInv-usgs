# # Prior to running this code:  
# - Download Sentinel-1 data from, e.g., ASF Vertex, and put in datadir (defined below)
# - Install ISCE software 



# import libraries  
import os
import glob


# directories
# basedir = '/data/anchorage/sentinel/p131f388/'
basedir = '/home/pburgi/anchorage/sentinel/p131f388/'
datadir = basedir + 'data/'
demdir  = basedir + 'dem/'

# bounding box of your region of interest, SNWE
bbox    = '61.26, 61.33, -150.6, -150.2' # SNWE 

## Specify dem file
demnm     = demdir + 'NEDtif/' + 'stitched.dem'

flist = [os.path.basename(x) for x in glob.glob(datadir + 'S1*')]
flist = [x[17:25] for x in flist]
masterdate = flist[0]

os.chdir(basedir)

# ## Co-register SLCs with ISCE stack processer 
# command = "stackSentinel.py -s ./data -o ./isce/precise/ -a ./isce/aux_cal/ -w ./slcs/ -d " + demnm + " -c 1 -n '1' -O 1 -m " + masterdate + " -b '" + bbox + "' -r 1 -z 1 -W slc"
# # os.system(command)

# # create executable file to run all the files in run_files, and run. 
# os.system('chmod 777 run_files/*')
# flist = [os.path.basename(x) for x in glob.glob(basedir + 'run_files/run*')]

# f = open('run_run_files', 'w')
# for i in flist:
#     f.write('./run_files/' + i)
#     f.write('\n')
# f.close()
# os.system('chmod 777 run_run_files')
# os.system('./run_run_files')


# make sure you have doVH.pl script 
os.system('./doVH.pl')

# for VH: create executable file to run all the files in run_files_vh, and run. 
os.system('chmod 777 run_files_vh/*')
flist = [os.path.basename(x) for x in glob.glob(basedir + 'run_files_vh/run*')]

f = open('run_run_files_vh', 'w')
for i in flist:
    f.write('./run_files_vh/' + i)
    f.write('\n')
f.close()
os.system('chmod 777 run_run_files_vh')
os.system('./run_run_files_vh')

os.system('mv merged/SLC merged/SLC_VH')



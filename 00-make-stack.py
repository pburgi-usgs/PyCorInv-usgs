# # Prior to running this code:  
# - Download Sentinel-1 data from, e.g., ASF Vertex, and put in datadir (defined below)
# - Install ISCE software 



# import libraries  
import os



# directories
# basedir = '/data/anchorage/sentinel/p131f388/'
basedir = '/home/pburgi/anchorage/sentinel/p131f388/'
datadir = basedir + 'data/'
demdir  = basedir + 'dem/'



# bounding box of your region of interest, SNWE
bbox    = [61.26, 61.33, -150.6, -150.2] # SNWE 



## Get DEM
# DEM bbox (bbox contained within, but all integers (i.e., no decimals))
dembbox    = [61, 62, -152, -148] # SNWE 
# Name of DEM file to fix xml, NEEDS TO BE CHANGED OR DONE A DIFFERENT WAY
demnm      = 'demLat_N' + str(dembbox[0]) + '_N' + str(dembbox[1]) + '_Lon_E' + str(dembbox[2])[1:] + '_E' + str(dembbox[3])[1:] + '.dem.wgs84'


# SRTM DEM source (-s): 1 if USA, 3 if global (this one is coarser)
demsource = '3'

# change dir to dem dir
os.chdir(demdir)

# get dem command
command =  'dem.py -a download -c -b ' + str(dembbox[0]) + ' ' + str(dembbox[1]) + ' ' + str(dembbox[2]) + ' ' + str(dembbox[3]) + ' -r -s ' + demsource 
print(command)
# os.system(command)

# stitch dem command
command2 = 'dem.py -a stitch -b ' + str(dembbox[0]) + ' ' + str(dembbox[1]) + ' ' + str(dembbox[2]) + ' ' + str(dembbox[3]) + ' -r -s ' + demsource + ' -l -k -c'
print(command2)
# os.system(command2)

# fix dem xml
command3 = 'fixImageXml.py -i ' + demnm + ' -f'
print(command3)
# os.system(command3)



## Co-register SLCs with ISCE stack processer 


# ### -Run ISCE to co-register SLCs, e.g.: 
# 
#     stackSentinel.py -s ./data -o ./isce/precise/ -a ./isce/aux_cal/ -w ./slcs/ -d ./dem/demLat_N18_N21_Lon_E054_E057.dem.wgs84 -c 1 -n '1' -O 1 -m 20180502 -b '19.19 19.20 55.39 55.4' -r 1 -z 1 -W slc
#  
#      
#   
#  
# ### -Run all files in run_files directory: 
# 
#     chmod 777 run_files/* 
#     
#     create executable file "run_run_files", with ./run_1_unpack_slc_topo_master; ./run_2_average_baseline... 
#     
#     run: ./run_run_files
#     
#     
# ### - Re-run ISCE for VH 
# 
#     run "doVH.pl" in workdir 
#     
#     chmod 777 run_files_vh/* 
#     
#     create executable file "run_run_files_vh", with ./run_1_unpack_slc_topo_master; ./run_7_geo2rdr_resample... 
#     
#     run: ./run_run_files_vh
#     
#     WHEN FINISHED, run: mv merged/SLC merged/SLC_VH
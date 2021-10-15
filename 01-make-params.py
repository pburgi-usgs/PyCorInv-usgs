
# coding: utf-8

# # Prior to running this code: 
# 
# 
# ### -Download Sentinel-1 data from, e.g., ASF Vertex
# 
# 
# 
# 
# ### -Download DEM, e.g.: 
# 
#     dem.py -a download -c -b 18 21 54 57  -r -s 3
#     
#     dem.py -a stitch -b 18 21 54 57  -r -s 3 -l -k -c
#     
#     fixImageXml.py -i demLat_N18_N21_Lon_E054_E057.dem.wgs84 -f
# 
# 
# 
# 
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

# In[1]:


import os
import glob
import xml.etree.ElementTree as ET
from datetime import date
import numpy as np


# In[2]:


#### INPUTS #### 

# Example inputs:
# Sentinel-1 T145
workdir   = '/data/pmb229/isce/Somalia/T145/'
dempath   = workdir+'dem/demLat_N08_N11_Lon_E046_E050.dem.wgs84'
mergeddir = workdir + 'merged/'
slcdir_vv = workdir + 'merged/' + 'SLC_VV/'
slcdir_vh = workdir + 'merged/' + 'SLC_VH/'
lam       = 0.056 # wavelength of sentinel c-band data


print('changing dirctory to: '+workdir)
wd     = os.getcwd()
os.chdir(workdir)


# In[3]:


#### Define date variables ####

flist = glob.glob(slcdir_vv + '2*')
flist = sorted(flist, key=lambda i: int(os.path.splitext(os.path.basename(i))[0]))
nd = len(flist)

dates = list()

for f in flist:
    dates.append(f[-8:]) 

dn = list()  
dec_year = list()
for d in dates:
    yr = d[0:4]
    mo = d[4:6]
    day = d[6:8]
    dt = date.toordinal(date(int(yr), int(mo), int(day)))
    dn.append(dt)
    d0 = date.toordinal(date(int(yr), 1, 1))
    doy = np.asarray(dt)-d0+1
    dec_year.append(float(yr) + (doy/365.25))
dn = np.asarray(dn)
dn0 = dn-dn[0] # make relative to first date


# In[4]:


#### Define track number #### 

# get first IW1 xml file 
flist = glob.glob(workdir + 'stack/' + 'IW*xml')
# this will sort only if the final thing from int(...) is a number. so int(...[0]) gives 'IW1', and int(../[0[2]]) gives '1'
flist = sorted(flist, key=lambda i: int(os.path.splitext(os.path.basename(i))[0][2]))


iw1 = flist[0]
# load it
tree = ET.parse(iw1) 
root = tree.getroot()
# turn it into a string
xmlstr = ET.tostring(root, encoding='utf8', method='xml')
xmlstr = str(xmlstr) 
# search string for track number
tnidx = xmlstr.find('tracknumber')
xmlstr2 = xmlstr[tnidx+36:tnidx+60]
tnidx2 =  xmlstr2.find('>')
tnidx3 =  xmlstr2.find('<')
# get track number
tracknum = xmlstr2[tnidx2+1:tnidx3]


# In[5]:


#### Define nx, ny #### 

# get first IW1 xml file 
flist = glob.glob(workdir + 'merged/geom_master/' + 'lon.rdr.hdr')

iw1 = flist[0]
# load it
hdrfile = open(iw1, 'r')
hdrfile = hdrfile.readlines()
samples = hdrfile[1]
nx  = samples[10:-1]
lines = hdrfile[2]
ny = lines[10:-1]

# define newnx, newny
alks = 4
rlks = 15
newnx = str(int(float(nx)/rlks))
newny = str(int(float(ny)/alks))


# In[6]:


#### Retrieve baselines #### 

flist = glob.glob(workdir + 'baselines/' + '2*_2*/')
flist = sorted(flist, key=os.path.dirname)


bpmean = list()
bpmean.append(float(0))
for f in flist:
    fn     = os.listdir(f)
    ffn    = str(f+fn[0])
    bltxt  = open(ffn, 'r')
    bllns  = bltxt.readlines()
    sidx = list()
    for f2 in bllns: 
        sid = 'Bperp' in f2
        sidx.append(sid)
    bptxt = [d for (d, remove) in zip(bllns, sidx) if remove]
    bpall = list()
    for f2 in bptxt: 
        bpall.append(float(f2[16:-1]))
    bpmean.append(np.mean(bpall))  
    


# In[7]:


#### Define and write params.npy ####

params = dict()
params['dates'] =        dates
params['dn'] =           dn
params['dn0'] =          dn0
params['nd'] =           nd
params['lam'] =          lam
params['alks'] =         alks
params['rlks'] =         rlks
params['ny'] =           ny
params['nx'] =           nx
params['newnx'] =        newnx
params['newny'] =        newny
params['dempath']   =    dempath
params['workdir'] =      workdir
params['mergeddir'] =    mergeddir
params['slcdir_vv'] =    slcdir_vv
params['slcdir_vh'] =    slcdir_vh
params['baselines'] =    bpmean

# Save the dictionary
np.save('params.npy',params)


# In[8]:


#### Finally, make sure to fix xmls of all SLCs ####
for i in dates:
    f = slcdir_vv+i+'/'+i+'.slc.full.xml'
    get_ipython().system(' fixImageXml.py -i $f -f  ')
for i in dates:
    f = slcdir_vh+i+'/'+i+'.slc.full.xml'
    get_ipython().system(' fixImageXml.py -i $f -f  ')


# In[ ]:


os.chdir(wd)


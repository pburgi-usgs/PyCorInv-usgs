# This code saves parameters that are used in the coherence inversion. 

# import libraries 
import os
import glob
import xml.etree.ElementTree as ET
from datetime import date
import numpy as np






#### INPUTS #### 

# Example inputs:
# Sentinel-1 T145
workdir   = '/home/pburgi/anchorage/sentinel/p131f388/'
dempath   = workdir + 'dem/NEDtif/stitched.dem'
mergeddir = workdir + 'merged/'
slcdir_vv = workdir + 'merged/' + 'SLC_VV/'
slcdir_vh = workdir + 'merged/' + 'SLC_VH/'
lam       = 0.056 # wavelength of sentinel c-band data


print('changing dirctory to: '+workdir)
wd     = os.getcwd()
os.chdir(workdir)





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





#### Define nx, ny #### 

# get first IW1 xml file 
flist = glob.glob(workdir + 'merged/geom_reference/' + 'lon.rdr.hdr')

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
n = alks*rlks





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
    

###### do vv and vh specific things ######


filenames = list()
for f in dates: 
    fn = slcdir_vv+f+'/'+f+'.slc.full'
    filenames.append(fn)

id1 = list()
id2 = list()
for i in range(len(dn)):
    for j in range(i,len(dn)):
        if [j] == [i]:
            pass
        else:
            id1.append(i)
            id2.append(j)

ids = tuple(zip(id1,id2))

# get diags
id2_2 = [i-1 for i in id2]
id1e = enumerate(id1)
id2e = enumerate(id2_2)
diags=list()
for i,j in zip(id1e, id2e): 
    if i == j:
        diags.append(i[0])

ni     = len(id1);

dn1 = [dn[i] for i in id1]
dn2 = [dn[i] for i in id2]
intdt = np.diff(dn)

# vv_params    = dict()
# vv_params['filenames'] =  filenames
# vv_params['id1'] =  id1
# vv_params['id2'] =  id2
# vv_params['ids'] =  ids
# vv_params['diags'] =  diags
# vv_params['ni'] =  ni
# vv_params['dn1'] =  dn1
# vv_params['dn2'] =  dn2
# vv_params['intdt'] =  intdt




#### Define and write params.npy ####

params = dict()
params['dates'] =        dates
params['dn'] =           dn
params['dn0'] =          dn0
params['nd'] =           nd
params['lam'] =          lam
params['alks'] =         alks
params['rlks'] =         rlks
params['n'] =            n
params['ny'] =           int(ny)
params['nx'] =           int(nx)
params['newnx'] =        int(newnx)
params['newny'] =        int(newny)
params['dempath']   =    dempath
params['workdir'] =      workdir
params['mergeddir'] =    mergeddir
params['slcdir_vv'] =    slcdir_vv
params['slcdir_vh'] =    slcdir_vh
params['baselines'] =    bpmean
params['id1']       =    id1
params['id2']       =    id2
params['ids']       =    ids
params['diags']     =    diags
params['ni']        =    ni
params['dn1']       =    dn1
params['dn2']       =    dn2
params['intdt']     =    intdt

# Save the dictionary
np.save('params.npy',params)






#### Finally, make sure to fix xmls of all SLCs ####
for i in dates:
    f = slcdir_vv+i+'/'+i+'.slc.full.xml'
    os.system(' fixImageXml.py -i ' + f + ' -f  ')
    
for i in dates:
    f = slcdir_vh+i+'/'+i+'.slc.full.xml'
    os.system(' fixImageXml.py -i ' + f + ' -f  ')




os.chdir(wd)


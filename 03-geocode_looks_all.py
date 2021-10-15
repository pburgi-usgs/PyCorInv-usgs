
# coding: utf-8

# In[4]:


import os
import glob
import numpy as np
#from ipynb.fs.full.corinvfuncs import *


# In[6]:


#### USER INPUT ####

# Example 
poli='_VH'
paramsnpy = '/data/pmb229/isce/Somalia/T145/params.npy'
bbox = '8.65 10.85 46.6 49.28' # NEED TO CHANGE BBOX FOR EACH FRAME 
r = 4  # rlooks
a = 4  # alooks





# get params, decide ints
wd     = os.getcwd()
params = np.load(paramsnpy, allow_pickle=True).item()
locals().update(params)
get_ipython().run_line_magic('run', 'decide_ints_stack.ipynb')

geodir = workdir+'geo'+poli+'/'
resdir = workdir+'results_dates'+poli+'/'


# In[7]:


# define function 

def geocoder(file,pol,resdir,bbox,dem,geodir):
    print('geocoding '+file+' '+pol)
    tmpfile = resdir+'tmp'
    resfile = resdir+file
    os.chdir(resdir)
    
    command = 'imageMath.py -e \'a\' -o '+ tmpfile +' --a=\'' + resfile+';' + str(newnx)+';float;1;BSQ\''

    get_ipython().system(' $command')
    get_ipython().system(' cp $resfile tmpfile')
    
    command = 'geocodeIsce.py -f '+tmpfile+' -b \''+ str(bbox)+'\' -d '+dem+' -m '+workdir+'master -s '+workdir+'master -r '+str(rlooks)+' -a '+str(alooks)
    get_ipython().system(' $command')
    
    command = 'chmod 777 '+ tmpfile + '*'
    get_ipython().system(' $command')
    
    command = 'mv '+tmpfile +'.geo ' + resfile + '.geo'
    get_ipython().system(' $command')
    command = 'mv '+tmpfile +'.geo.xml ' + resfile + '.geo.xml'
    get_ipython().system(' $command')
    command = 'mv '+tmpfile +'.geo.vrt ' + resfile + '.geo.vrt'
    get_ipython().system(' $command')
    
    command = 'fixImageXml.py -i '+resfile+'.geo -b'
    get_ipython().system(' $command')
    
    os.chdir(workdir)
    


# In[8]:


if not os.path.isdir(geodir):
    print('creating directory '+geodir)
    get_ipython().system(' mkdir $geodir')


# In[11]:


filelist  = glob.glob(resdir + '*cor')
nfiles    = len(filelist)

for i in range(nfiles):
    file = os.path.basename(filelist[i])
    if os.path.isfile(resdir+file+'.geo') | os.path.isfile(geodir+file+'.geo'):
        print(file + ' already geocoded')
    else:
        geocoder(file,pol,resdir,bbox,dempath,geodir)
        command = 'mv '+filelist[i]+'.geo*'+ ' '+geodir
        get_ipython().system(' $command')
        


# In[12]:


if os.path.isfile(geodir+'rows.geo'):
    print('rows already geocoded')
else:
    rowfile = resdir+'rows'
    fid = open(rowfile, 'w')
    get_ipython().system(' chmod 777 $rowfile')
    for i in range(1,newny+1):
        rs  = np.ones((1,newnx)).flatten()*i
        rs  = rs.astype('float32')
        rs.tofile(fid)
    fid.close()
    geocoder('rows','',resdir,bbox,dempath,geodir)
    command = 'mv '+rowfile+'.geo* '+geodir
    get_ipython().system(' $command')
    
if os.path.isfile(geodir+'cols.geo'):
    print('cols already geocoded')
else:
    colfile = resdir+'cols'
    fid2 = open(colfile, 'w')
    get_ipython().system(' chmod 777 $colfile')
    for i in range(newny):
        rs2  = np.array(list(range(1,newnx+1))).astype('float32')
        rs2.tofile(fid2)
    fid2.close()
    geocoder('cols','',resdir,bbox,dempath,geodir)
    command = 'mv '+colfile+'.geo* '+geodir
    get_ipython().system(' $command')

if os.path.isfile(resdir+'tmp'):
    command ='rm '+resdir+'tmp*'
    get_ipython().system(' $command')


# In[13]:


# start code look_geo.m

# get nx_geo, ny_geo
f = geodir + 'c0.cor.geo.vrt'
v = open(f, 'r')
v = v.readlines()
l1 = v[0]
qs = [i for i in range(len(l1)) if l1.startswith('\"', i)]

nx_geo = int(l1[qs[0]+1:qs[1]])
ny_geo = int(l1[qs[2]+1:qs[3]])


# In[14]:


files  = glob.glob(resdir + '*.cor')
os.chdir(geodir)
for j in files:
    file    = os.path.basename(j)
    newfile = file[0:-4]+'_'+str(r)+'r_'+str(a)+'a.cor.geo'
    oldfile = geodir+file+'.geo'
    if not os.path.isfile(geodir+newfile):
        fidi = open(oldfile,'r')
        fidr = open(geodir+'rows.geo', 'r')
        fido = open(geodir+'tmp', 'w')
        
        for k in range(ny_geo):
            tmp1 = np.fromfile(fidi, dtype=np.float32, count=nx_geo)
            tmp2 = np.fromfile(fidr, dtype=np.float32, count=nx_geo)
            tmp1[tmp2==0] = np.nan
            tmp1.tofile(fido)
        command = 'mv tmp '+oldfile
        fidi.close()
        fidr.close()
        fido.close()
        
        command = 'gdal_translate '+oldfile+'.vrt '+oldfile+'.tif'
        get_ipython().system(' $command')
        
        command = 'looks.py -i '+oldfile+' -o '+newfile+' -r '+str(r)+' -a '+str(a)
        get_ipython().system(' $command')
        command = 'chmod 777 *'
        get_ipython().system(' $command')
    else:
        print('already looked down '+newfile)
        
os.chdir(workdir)


# In[15]:


# geocode lon/lat radar files 

lonfileold=workdir+'merged/geom_master/lon.rdr.full';
latfileold=workdir+'merged/geom_master/lat.rdr.full';
lonfilenew=workdir+'merged/geom_master/lon.rdr.4alks_15rlks.full'
latfilenew=workdir+'merged/geom_master/lat.rdr.4alks_15rlks.full'

command = 'looks.py -i '+lonfileold+' -o '+lonfilenew+' -r '+str(rlks)+' -a '+str(alks)
get_ipython().system(' $command')
command = 'looks.py -i '+latfileold+' -o '+latfilenew+' -r '+str(rlks)+' -a '+str(alks)
get_ipython().system(' $command')


# In[16]:


os.chdir(wd)


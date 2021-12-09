

import os
import glob
import numpy as np



#### USER INPUT ####

# Example 
poli='_VV'
pol = poli
paramsnpy  = '/home/pburgi/anchorage/sentinel/p131f388/params.npy'
# bbox = '8.65 10.85 46.6 49.28' # NEED TO CHANGE BBOX FOR EACH FRAME 
bbox = '60.995 61.674 -150.786 -148.911' # NEED TO CHANGE BBOX FOR EACH FRAME 
r = 4  # rlooks
a = 4  # alooks





# get params, decide ints
wd     = os.getcwd()
params = np.load(paramsnpy, allow_pickle=True).item()
locals().update(params)


if poli == '_VV':
    slcdir = slcdir_vv
else:
    slcdir = slcdir_vh

geodir = workdir+'geo'+poli+'/'
resdir = workdir+'results_dates'+poli+'/'




# define function 

def geocoder(file,pol,resdir,bbox,dem,geodir):
    print('geocoding '+file+' '+pol)
    tmpfile = resdir+'tmp'
    resfile = resdir+file
    os.chdir(resdir)
    
    command = 'imageMath.py -e \'a\' -o '+ tmpfile +' --a=\'' + resfile+';' + str(newnx)+';float;1;BSQ\''

    os.system(command)
    os.system('cp ' + resfile + ' ' + tmpfile)
    
    command = 'geocodeIsce.py -f '+tmpfile+' -b \''+ str(bbox)+'\' -d '+dem+' -m '+workdir+'reference -s '+workdir+'reference -r '+str(rlks)+' -a '+str(alks)
    os.system(command)
    
    command = 'chmod 777 '+ tmpfile + '*'
    os.system(command)
    
    command = 'mv '+tmpfile +'.geo ' + resfile + '.geo'
    os.system(command)
    command = 'mv '+tmpfile +'.geo.xml ' + resfile + '.geo.xml'
    os.system(command)
    command = 'mv '+tmpfile +'.geo.vrt ' + resfile + '.geo.vrt'
    os.system(command)
    
    command = 'fixImageXml.py -i '+resfile+'.geo -b'
    os.system(command)
    
    os.chdir(workdir)






if not os.path.isdir(geodir):
    print('creating directory '+geodir)
    os.system(' mkdir ' + geodir)






filelist  = glob.glob(resdir + '*cor')
nfiles    = len(filelist)

for i in range(nfiles):
    file = os.path.basename(filelist[i])
    if os.path.isfile(resdir+file+'.geo') | os.path.isfile(geodir+file+'.geo'):
        print(file + ' already geocoded')
    else:
        geocoder(file,pol,resdir,bbox,dempath,geodir)
        command = 'mv '+filelist[i]+'.geo*'+ ' '+geodir
        os.system(command)
        





if os.path.isfile(geodir+'rows.geo'):
    print('rows already geocoded')
else:
    rowfile = resdir+'rows'
    fid = open(rowfile, 'w')
    os.system(' chmod 777 ' + rowfile)
    for i in range(1,newny+1):
        rs  = np.ones((1,newnx)).flatten()*i
        rs  = rs.astype('float32')
        rs.tofile(fid)
    fid.close()
    geocoder('rows','',resdir,bbox,dempath,geodir)
    command = 'mv '+rowfile+'.geo* '+geodir
    os.system(command)
    
if os.path.isfile(geodir+'cols.geo'):
    print('cols already geocoded')
else:
    colfile = resdir+'cols'
    fid2 = open(colfile, 'w')
    os.system(' chmod 777 ' + colfile)
    for i in range(newny):
        rs2  = np.array(list(range(1,newnx+1))).astype('float32')
        rs2.tofile(fid2)
    fid2.close()
    geocoder('cols','',resdir,bbox,dempath,geodir)
    command = 'mv '+colfile+'.geo* '+geodir
    os.system(command)

if os.path.isfile(resdir+'tmp'):
    command ='rm '+resdir+'tmp*'
    os.system(command)






# start code look_geo.m

# get nx_geo, ny_geo
f = geodir + 'c0.cor.geo.vrt'
v = open(f, 'r')
v = v.readlines()
l1 = v[0]
qs = [i for i in range(len(l1)) if l1.startswith('\"', i)]

nx_geo = int(l1[qs[0]+1:qs[1]])
ny_geo = int(l1[qs[2]+1:qs[3]])







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
        os.system(command)
        
        command = 'looks.py -i '+oldfile+' -o '+newfile+' -r '+str(r)+' -a '+str(a)
        os.system(command)
        command = 'chmod 777 *'
        os.system(command)
    else:
        print('already looked down '+newfile)
        
os.chdir(workdir)







# geocode lon/lat radar files 

lonfileold=workdir+'merged/geom_reference/lon.rdr.full';
latfileold=workdir+'merged/geom_reference/lat.rdr.full';
lonfilenew=workdir+'merged/geom_reference/lon.rdr.4alks_15rlks.full'
latfilenew=workdir+'merged/geom_reference/lat.rdr.4alks_15rlks.full'

command = 'looks.py -i '+lonfileold+' -o '+lonfilenew+' -r '+str(rlks)+' -a '+str(alks)
os.system(command)
command = 'looks.py -i '+latfileold+' -o '+latfilenew+' -r '+str(rlks)+' -a '+str(alks)
os.system(command)





os.chdir(wd)


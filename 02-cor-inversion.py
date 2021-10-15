
# coding: utf-8

# In[ ]:


# 02-cor-inversion


# In[1]:


import os
import numpy as np
import cmath
from ipynb.fs.full.corinvfuncs import *
import time


# In[2]:


#### INPUT REQUIRED ####

poli       = '_VH'
paramsnpy  = '/data/pmb229/isce/Somalia/T145/params.npy'
# Shape of window used for coherence determination, 0=triangle, 1=box car, 2=Gaussian
windowtype = 0


# load params, decide ints 
params = np.load(paramsnpy, allow_pickle=True).item()
locals().update(params)
get_ipython().run_line_magic('run', 'decide_ints_stack.ipynb')
wd     = os.getcwd()

print('nx:', nx, ' ny:',ny)


# In[3]:


#### Define variables needed in inversion ####

bpr  = [baselines[i]-baselines[j] for i,j in zip(id1,id2)]
abpr = [abs(i) for i in bpr]
bpw  = 200; #weights for baseline estimation

rx        = rlooks;
ry        = alooks;

rangevec  = list(range(1,int(newnx)+1))
rangevec  = np.array([i*rx-np.floor(rx/2)-1 for i in rangevec])
azvec     = list(range(1,int(newny)+1))
azvec     = np.array([i*ry-np.floor(ry/2)-1 for i in azvec])

dn        = np.array(dn)
dni       = dn[0:nd-1]+np.diff(dn)/2;
intdt     = np.diff(dn);

# alpha    = 50;
im       = cmath.sqrt(-1)

cidl     = np.tril(np.ones((nd,nd)),-1)
errslope = 0.3;
mncor    = errslope/(1+errslope);
mncorl   = np.log(mncor);


# In[4]:


# Window types
windowtype = 0
if windowtype == 0: # triangle
    windx = np.concatenate([np.arange(1/(rx+1), 1.01, 1/(rx+1)), np.arange((1-1/(rx+1)), (1/(rx+1))-0.01, -1/(rx+1))])
    windy = np.concatenate([np.arange(1/(ry+1), 1.01, 1/(ry+1)), np.arange((1-1/(ry+1)), (1/(ry+1))-0.01, -1/(ry+1))])
elif windowtype == 1: # boxcar
    windx = np.zeros([1,rx*2+1])[0]
    windx[int(np.floor(rx/2))-1:int(np.ceil(rx/2)+rx)]=1
    windy = np.zeros([1,ry*2+1])[0]
    windy[int(np.floor(ry/2))-1:int(np.ceil(ry/2)+ry)]=1
elif windowtype == 2: # Gaussian
    windx=np.exp(-np.arange(-rx,rx+1,1)**2/2/(rx/2)**2)
    windy=np.exp(-np.arange(-ry,ry+1,1)**2/2/(ry/2)**2)

windx=windx/np.sum(windx);
windy=windy/np.sum(windy);

ry=np.floor(len(windy)/2);


# In[ ]:


# Open all slcs

fidi = list()
for i in dates:
    f = slcdir+i+'/'+i+'.slc.full'
    fidi.append(open(f, 'r'))


# In[ ]:


# Make results directory

adir     = workdir+'results_dates'+pol+'/'
if not os.path.isdir(adir):
    print('creating directory '+adir)
    get_ipython().system(' mkdir $adir')


# In[6]:


# Open all result files 

c0 = adir+'c0.cor'
fidr = list()
fidp = list()
if os.path.isfile(c0):
    fid0 = open(c0, 'r')
    for j in range(int(newny)):
        a = np.fromfile(fid0, dtype=np.float32, count=int(newnx))
        if len(a) < int(newnx):
            break 
    fid0.close()
    online = j
    if online < 1:
        print('c0.cor empty?')
        
    for i in range(nd):
        fidr.append(open(adir+'rel_'+dates[i]+'.cor', 'a'))
    for i in range(nd-1):
        fidp.append(open(adir+'perm_'+dates[i]+'_'+dates[i+1]+'.cor', 'a'))
    fid0 = open(adir+'c0.cor', 'a')
    fid1 = open(adir+'rms.cor', 'a')
    fidmin = open(adir+'cmin.cor', 'a')
else:
    online = 0
    for i in range(nd):
        fidr.append(open(adir+'rel_'+dates[i]+'.cor', 'w'))
    for i in range(nd-1):
        fidp.append(open(adir+'perm_'+dates[i]+'_'+dates[i+1]+'.cor', 'w'))
    fid0 = open(adir+'c0.cor', 'w')
    fid1 = open(adir+'rms.cor', 'w')
    fidmin = open(adir+'cmin.cor', 'w')
    chmodfiles = adir+'*'
    get_ipython().system(' chmod 666 $chmodfiles')


# In[5]:


# Define design matrices 

Gi0 = np.zeros((ni,nd-1))
for i in range(ni):
    Gi0[i,id1[i]:id2[i]] = 1

Gr0 = np.zeros((ni,nd))
for i in range(ni):
    Gr0[i,id1[i]] = 1
    Gr0[i,id2[i]] = -1

Gr = Gr0[:,1:]


# In[ ]:


#### START INVERSION ####

for j in range(online,int(newny)):
    print('on row', j, '/', newny)

    if j == 0:
        readl    = ry
        startbit = 0
        starty   = 0
    else:
        readl    = ry*2+1;
        starty   = (j)*ry-np.ceil(ry/2);
        startbit = starty*nx*8; 

    slcs = np.zeros((int(nx),int(ry*2+1),int(nd))).astype(np.complex)
    slcs[:,:,:] = np.nan
    c = int(int(nx)*2*readl)
    for i in range(nd): 
        fidi[i].seek(startbit, 0)
        tmp = np.fromfile(fidi[i], dtype=np.float32, count=c).reshape(int(readl),int(nx*2)).transpose()
        cpx = tmp[0::2]+im*tmp[1::2]

        if j == int(newny):
            nana      = np.zeros((len(cpx),int(ry*2+1)-np.ma.size(cpx,axis=1)))
            nana[:,:] = np.nan
            cpx       = np.concatenate((cpx,nana), axis=1)
        elif j == 0:
            nana      = np.zeros((int(nx),int(ry+1)))
            nana[:,:] = np.nan
            cpx       = np.concatenate((cpx, nana), axis=1)

        slcs[:,:,i]=cpx

    count = -1
    cors = np.zeros((int(ni),int(newnx)))
    cors[:,:] = np.nan
    for i in range(nd-1):
        slc1 = slcs[:,:,i]
        for k in range(i+1,nd):
            count = count + 1
            slc2 = slcs[:,:,k]
            a = np.multiply(slc1, np.conjugate(slc1))
            b = np.multiply(slc2, np.conjugate(slc2))
            c = np.multiply(slc1, np.conjugate(slc2))
            a = np.matmul(windy,a.transpose())
            b = np.matmul(windy,b.transpose())
            c = np.matmul(windy,c.transpose())

            asum = np.convolve(a,windx,mode='same')
            bsum = np.convolve(b,windx,mode='same')
            csum = np.convolve(c,windx,mode='same')

            cpx3 = np.array(np.divide(csum, np.sqrt(np.multiply(asum, bsum)))) # 54
            cpx4 = list()
            [cpx4.append(cpx3[int(ll)]) for ll in rangevec]
            cpx3 = np.array(cpx4)

            sm   = np.abs(cpx3)
            sm[np.isnan(sm)] = 0

            cors[count,:] = sm

    good         = cors>0
    bad          = cors<=0
    cors[cors>1] = 1
    cors[bad]    = np.nan
    ngood        = np.sum(good,axis=0);
    goodid       = np.argwhere(ngood>=10)
    gcount       = cors>mncor # 70
    gcount       = gcount.astype('int').astype('float')
    gcount       = np.nansum(gcount,axis=0)

    allm0        = np.zeros((int(nd*2+2), int(newnx)))
    allm0[:,:]   = np.nan

    if goodid.size != 0:
        permbad = np.tile(False, (int(ni), int(newnx)))
        doperm  = np.where((gcount>0) & (gcount<ni*0.98))
        doperm = np.array(doperm).flatten()
        corsdd = cors[:,doperm].squeeze()
        crrslts = countrows(id1,id2,corsdd,mncorl,mncor,Gi0)
        permbad[:,doperm] = crrslts

        t0      = np.zeros((1,len(goodid)))
        t0[:,:] = np.nan
        t0      = t0.flatten()
        t1      = np.zeros((int(nd-1), len(goodid)))
        t1[:,:] = np.nan
        t2      = np.zeros((int(nd), len(goodid)))
        t2[:,:] = np.nan
        t3      = np.zeros((1,len(goodid)))
        t3[:,:] = np.nan
        t3      = t3.flatten()
        t4      = np.zeros((1,len(goodid)))
        t4[:,:] = np.nan
        t4      = t4.flatten()

        t = time.time()
        for i in range(len(goodid)):
            data         = cors[:,goodid[i]]
            derr         = errslope*(1-data)
            dmin         = data-derr
            dmin[dmin<0] = 1e-10
            dmax         = data+derr 

            d     = np.log(data)
            dlmin = np.log(dmin)
            dlmax = np.log(dmax)
            derr  = dlmax-d
            dderr = d-derr
            pbi   = permbad[:,goodid[i]]

            gooddat, Grstat, Gistat = find_bad(dderr,diags,pbi,Gr0,Gi0);

            datag = d[gooddat]
            c0    = mymax(datag,100)

            cpmin = np.zeros((int(nd-1)))
            w     = np.exp(100*dlmin)
            dw    = dlmin*w


            for k in range(nd-1):
                idd       = (np.isfinite(dw).flatten()) & (Gi0[:,k]==1)
                cpmin[k] = np.sum(dw[idd])/np.sum(w[idd])

            diagsf         = np.array(diags)
            cpmin[~Gistat] = d[diagsf[~Gistat]].flatten()-c0
            cpmin          = np.minimum(0,cpmin)

            cp1            = est_ct(d,Gi0,cpmin)
            cp1[~Gistat]   = np.minimum(0,d[diagsf[~Gistat]]-c0).flatten()


            synp           = np.matmul(Gi0,cp1.transpose())
            gooddat        = gooddat.flatten()
            synp[~gooddat] = np.nan
            d              = d.flatten()
            c0             = np.minimum(0,mymax(d-synp,25))
            cres           = d-synp-c0;


            cr1            = est_cr(cres,np.exp(synp),nd,cidl)
            cr1[~Grstat]   = np.nan
            cshifts1,cp2   = flatten_front(cr1,25,cp1,cpmin)
            cp2[~Gistat]   = np.minimum(0,d[diagsf[~Gistat]]-c0)

            synp           = np.matmul(Gi0,cp2)
            synp[~gooddat] = np.nan
            cres           = d-synp-c0

            cr2            = est_cr(cres,np.exp(synp),nd,cidl)
            cr2[~Grstat]   = np.nan
            cshifts2,cp    = flatten_back(cr2,25,cp2,cpmin)
            cp[~Gistat]    = np.minimum(0,d[diagsf[~Gistat]]-c0)

            synp           = np.matmul(Gi0,cp)
            synp[~gooddat] = np.nan
            cres           = d-synp-c0
            cr             = est_cr(cres,np.exp(synp),nd,cidl)
            cshifts,cp     = flatten_front(cr,25,cp,cpmin)
            cr             = cr-cshifts
            cp[~Gistat]    = np.minimum(0,d[diagsf[~Gistat]]-c0)
            cshifts,cp     = flatten_back(cr,25,cp,cpmin)
            cr             = cr-cshifts
            cp[~Gistat]    = np.minimum(0,d[diagsf[~Gistat]]-c0)

            res            = d-np.matmul(Gi0, cp)+ np.abs(np.matmul(Gr0,cr))-c0
            cr             = cr-mymax(cr,50);

            t0[i]   = np.exp(c0)
            t1[:,i] = np.exp(cp)
            t2[:,i] = np.exp(cr)
            t3[i]   = np.sqrt(np.mean((res[gooddat])**2))
            t4[i]   = 1-mymax(1-data,100)

        elapsed    = time.time() - t

        # bookkeeping
        goodid = goodid.flatten()
        allm0[0,goodid]         = t0
        allm0[1:nd,goodid]      = t1
        allm0[nd:nd*2,goodid]   = t2
        allm0[-2,goodid]        = t3
        allm0[-1,goodid]        = t4

    allm0  = allm0.astype('float32')
    allm0[0,:].tofile(fid0)
    for i in range(nd-1):
        allm0[1+i,:].tofile(fidp[i])
    for i in range(nd):
        allm0[nd+i,:].tofile(fidr[i])

    allm0[-2,:].tofile(fid1)
    allm0[-1,:].tofile(fidmin)


fid0.close()
fid1.close()
fidmin.close()
for i in range(nd-1):
    fidp[i].close()  
for i in range(nd):
    fidr[i].close()


# In[ ]:


os.chdir(wd)


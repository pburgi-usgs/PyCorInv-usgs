
# coding: utf-8

# In[1]:


import numpy as np
def countrows(id1,id2,cors,mncorl,mncor,Gi0):
    [ni,nx] = cors.shape
    medrect = np.zeros((int(ni), int(nx)))
    nbef    = np.zeros((int(ni), int(nx)))
    cbef    = np.zeros((int(ni), int(nx)))
    d       = np.log(cors).transpose()
    d[d == -np.inf] = np.nan
    id1     = np.array(id1)
    id2     = np.array(id2)

    for k in range(ni):
        recid  = (id1<=id1[k]) & (id2>=id2[k])
        befids = (id1==id1[k]) & (id2<=id2[k])

        medrect[k,:] = np.nanmean(d[:,recid],axis=1)
        nbef[k,:]    = np.sum(befids)
        cbef[k,:]    = np.nansum(d[:,befids]>mncorl,axis=1)
    ratio=cbef/nbef
    mclow   = np.log(mncor*1.5)
    permbad = (medrect<mclow) & (ratio<0.85)
    permbad = (permbad==True) | (np.isnan(cors))
    
    return permbad


# In[2]:


def mymax(datag,alpha):
    iiii  = np.isfinite(datag)
    di    = datag[iiii] 
    ww    = np.exp(alpha*di)
    mymax = np.sum(np.matmul(di,ww))/np.sum(ww)
    return mymax


# In[4]:


def mymed(crs,wgts):
    [ndd,nxx] = crs.shape
    cutoff = 0.02 # cutoff weight
    wgts[wgts<cutoff] = np.nan
    if (ndd == 1):
        value = crs
    else:
        sortid       = crs.argsort(axis=0)
        s            = crs[sortid, np.arange(sortid.shape[1])]

        # note: not doing the "if nargin=2" step
        ws      = wgts/np.tile(np.nansum(wgts,axis=0),(ndd,1))
        iss     = np.tile(range(nxx),(ndd,1))
        sortid2 = np.concatenate((sortid.transpose()), axis=None)
        is2     = np.concatenate((iss.transpose()), axis=None)
        wsa     = ws[sortid2,is2].reshape([ndd, nxx]).transpose()
        wss     = np.nancumsum(wsa, axis=0)
        idd     = np.nanargmin(np.abs(wss-0.5), axis=0)

        value = s[idd,list(range(nxx))]
        
    return value


# In[5]:


def est_cr(cres, synth, nd, cidl): 
    cidli         = np.where(cidl.transpose()==1)
    cidli2        = tuple((cidli[1],cidli[0]))
    crs           = np.zeros((int(nd), int(nd)))
    crs[cidli2]   = cres.flatten()
    crs           = crs+crs.transpose()   
    crs[crs==0]   = np.nan
    
    if np.all(synth==0):
        cerr = 0.3083*(1-crs)-0.2*(1-crs)**2
        wgts = 1/cerr
    else: 
        wgts          = np.zeros((int(nd),int(nd)))
        wgts[cidli2]  = synth # 0 to 1
        wgts          = wgts+wgts.transpose()
        wgts[wgts==0] = np.nan
        wgts          = np.exp((wgts-1)*5)  # scalar makes near 0.1 at synth=0.5;
    cr = mymed(crs,wgts)

    aa = np.tile(cr,(nd,1))
    ab = np.tile(cr,(nd,1)).transpose()
    a  = aa-ab
    b  = aa
    c  = -np.abs(a)-b
    d  = crs-c
    crsnew = -np.abs(d)


    cr2      = mymed(crsnew,wgts)
    return cr2


# In[4]:


def est_ct(d,Gi,cpmin): 
    nd     = Gi.shape[1]
    nd    += 1
    alpha  = 100
    cidl        = np.tril(np.ones((nd,nd)), -1)
    cidli       = np.where(cidl.transpose()==1)
    cidli2      = tuple((cidli[1], cidli[0]))
    jnk         = np.zeros((nd,nd))
    jnk[:,:]    = np.nan
    jnk[cidli2] = d.flatten()
    jumps       = np.nanmean(np.diff(jnk, axis=0).transpose(), axis=0)
    jumps[0]    = jumps[1]
    ct_est      = np.zeros((1,nd-1)).flatten()
    sortid      = np.argsort(jumps)
    s           = np.sort(jumps)
    sortid      = sortid[s<0]
    for i in sortid:
        w    = np.exp(alpha*d)
        dw   = d*w
        idd  = (np.isfinite(d)).flatten() & (Gi[:,i]==1)
        idn  = (np.isfinite(d)).flatten() & (Gi[:,i]==0)
        n    = sum(idd)
        if n > 1: 
            c1  = np.sum(dw[idd])/np.sum(w[idd])
            c2  = np.sum(dw[idn])/np.sum(w[idn])
        elif sum(idd) == 0:
            c1 = 0
            c2 = 0
        else: 
            c1 = max(d[idd])
            c2 = min(d[idd])

        ct_est[i] = np.minimum(0,c1-c2)
        ct_est[i] = np.maximum(cpmin[i], ct_est[i])
        syn       = Gi[:,i]*ct_est[i]
        d         = d.flatten()-syn
    return ct_est


# In[5]:


def find_bad(dderr,diags,pbi,Gr0,Gi0):
    # use these data
    gooddat =~ pbi
    gooddat[diags] = 1
    gooddat[np.isnan(dderr)] = 0

    # invert for these model params
    Grstat = np.sum(np.abs(Gr0[gooddat.flatten(),:]),axis=0)>2
    Gistat = np.sum(Gi0[gooddat.flatten(),:],axis=0)>1
    return gooddat, Grstat,Gistat


# In[ ]:


def flatten_front(cmed,alpha,cp,cpmin):
    ndd = len(cmed)
    crm = list()
    for ii in range(ndd):
        crm.append(mymax(cmed[0:ii+1],alpha))
    crm          = np.array(crm)
    smaller      = np.argwhere(cmed[1:-1]<crm[0:-2]).flatten()+1
    crm[smaller] = crm[smaller+1]
    crm          = np.maximum.accumulate(crm) 

    crm[-1]      = crm[-2]
    crm[0]       = crm[1]
    cdif         = -np.abs(np.diff(crm))
    cdif[np.isnan(cdif)] = 0
     # not doing if nargin>2 statement
    testcp = cp+cdif
    badi   = testcp < cpmin
    if sum(badi)>0:
        badi       = np.argwhere(badi == True)
        bdif       = cpmin[badi]-testcp[badi]
        cdif[badi] = cdif[badi]+bdif
        rbadi      = len(badi)
        for ii in range(rbadi):
            crm[0:badi[ii,0]+1] = crm[0:badi[ii,0]+1]+bdif[ii]
    cp = cp+cdif
    
    return crm,cp


# In[ ]:


def flatten_back(cmed,alpha,cp,cpmin):
    ndd = len(cmed)
    crm = list()
    for ii in range(ndd):
        crm.append(mymax(cmed[ii:],alpha))
    crm = np.flipud(crm)
    crm          = np.fmax.accumulate(crm)
    crm  = np.flipud(crm)

    crm[-1]      = crm[-2]
    crm[0]       = crm[1]

    cdif         = -np.abs(np.diff(crm))
    cdif[np.isnan(cdif)] = 0
    # not doing if nargin>2 statement
    testcp = cp+cdif
    badi   = testcp < cpmin
    if sum(badi)>0:
        badi       = np.argwhere(badi == True)
        bdif       = cpmin[badi]-testcp[badi]
        cdif[badi] = cdif[badi]+bdif
        rbadi      = len(badi)
        for ii in range(rbadi):
            crm[badi[ii,0]+1:] = crm[badi[ii,0]+1:]+bdif[ii]
    cp = cp+cdif
    return crm, cp
        



# coding: utf-8

# In[ ]:


#### NOTE ####
# THIS NOTEBOOK ONLY WORKS WHEN RUN FROM OTHER NOTEBOOKS THAT HAVE PRE-DEFINED SEVERAL OTHER VARIABLES, E.G.: 
# 02-cor-inversion, 03-geocode_looks_all, plot_inv_results


# In[10]:


import numpy as np


# In[11]:


# functions
def decidepol(poli):
    if poli == '_VV':
        pol = '_VV'
    else:
        pol = '_VH'
    return pol

def decideproject(paramspny): 
    params = np.load(paramsnpy).item()
    return params
    


# In[1]:


get_ipython().run_cell_magic('capture', '', "# uncomment above line if you would like the 'params' dictionary printed to the screen.\n\npol    = decidepol(poli)\nparams = decideproject(paramsnpy)\nlocals().update(params)\n\n\nnewnx  = int(newnx)\nnewny  = int(newny)\nnx     = int(nx)\nny     = int(ny)\n\nif pol == '_VV': \n    slcdir = slcdir_vv\nelse: \n    slcdir = slcdir_vh\n        \nprint(params)")


# In[13]:



filenames = list()
for f in dates: 
    fn = slcdir+f+'/'+f+'.slc.full'
    filenames.append(fn)


# In[5]:


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

alooks = alks
rlooks = rlks
n      = rlooks*alooks;


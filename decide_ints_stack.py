


#### NOTE ####
# THIS NOTEBOOK ONLY WORKS WHEN RUN FROM OTHER NOTEBOOKS THAT HAVE PRE-DEFINED SEVERAL OTHER VARIABLES, E.G.: 
# 02-cor-inversion, 03-geocode_looks_all, plot_inv_results



import numpy as np


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



pol    = decidepol(poli)
params = decideproject(paramsnpy)
locals().update(params)

if pol == '_VV':
    slcdir = slcdir_vv
else:
    slcdir = slcdir_vh
        
print(params)




filenames = list()
for f in dates: 
    fn = slcdir+f+'/'+f+'.slc.full'
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


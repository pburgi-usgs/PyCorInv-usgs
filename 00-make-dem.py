# # Prior to running this code:  
# - This code is only if you can't run dem.py, which gets SRTM DEMs for you
# - Get all tiles of, e.g., NED, IFSAR DEM in geotiff format, and put in demdir folder
# - Install ISCE software 



# import libraries  
import os
import glob
import xml.etree.ElementTree as ET
import rasterio
import isce
import isceobj




# directories
# basedir = '/data/anchorage/sentinel/p131f388/'
basedir = '/home/pburgi/anchorage/sentinel/p131f388/'
datadir = basedir + 'data/'
demdir  = basedir + 'dem/NEDtif/'

# change dir to dem dir
os.chdir(demdir)

# geotiff: get files to be translated
flist = glob.glob(demdir + '*tif')

for d in flist:
    os.system('gdalbuildvrt ' + d + '.vrt ' + d)
    dr = d[0:-4]
    drr = d[-19:-4]
    print(drr)
    os.system('gdal_translate  -of ENVI -ot Int16 ' + d + '.vrt ' + dr + '.dem.nad83')
    os.system('gdalbuildvrt ' + dr + '.dem.nad83.vrt ' + dr + '.dem.nad83')
    os.system('gdalwarp -t_srs EPSG:4326 -of vrt ' + dr +'.dem.nad83 ' + dr + '.dem.wgs84.vrt')
    os.system('gdal_translate -of ENVI ' + dr + '.dem.wgs84.vrt ' + dr + '.dem.wgs84')
    # make isce xml 
    data = rasterio.open(dr + '.dem.wgs84.vrt')
    width = data.width
    trans = data.transform
    startLon = trans[2]
    deltaLon  = trans[0]
    length = data.height
    startLat = trans[5]
    deltaLat = trans[4]

    objdem = isceobj.createDemImage()
    objdem.setFilename(dr + '.dem.wgs84')
    objdem.setWidth(width)
    objdem.scheme = 'BIP'
    objdem.setAccessMode('read')
    objdem.imageType = 'dem'
    objdem.dataType = 'short'
    objdem.bands = 1
    dictProp = {'REFERENCE': 'WGS84', 'Coordinate1': \
                {'size': width, 'startingValue':startLon, 'delta':deltaLon}, \
                'Coordinate2': {'size': length, 'startingValue': startLat,  'delta':deltaLat}, \
                    'FILE_NAME': drr + '.dem.wgs84'}
    objdem.init(dictProp)
    objdem.renderHdr()
    # look down
    os.system('looks.py -i ' + dr + '.dem.wgs84 -o ' + dr + '_looked.dem.wgs84 -r 5 -a 5')

    os.system('rm *nad83*')
    os.system('rm *hdr')
    os.system('rm *tif.vrt')
    os.system('rm ' + dr + '.dem.wgs84*')


# stitch dem
os.system('gdalbuildvrt -srcnodata -9988 out.dem.vrt *looked.dem.wgs84.vrt')
os.system('gdal_translate -of ENVI -a_nodata -9988 out.dem.vrt stitched.dem')
os.system('gdalbuildvrt -srcnodata -9988 stitched.dem.vrt stitched.dem')
# make isce xml 
data = rasterio.open('stitched.dem.vrt')
width = data.width
trans = data.transform
startLon = trans[2]
deltaLon  = trans[0]
length = data.height
startLat = trans[5]
deltaLat = trans[4]
objdem = isceobj.createDemImage()
objdem.setFilename('stitched.dem')
objdem.setWidth(width)
objdem.scheme = 'BIP'
objdem.setAccessMode('read')
objdem.imageType = 'dem'
objdem.dataType = 'short'
objdem.bands = 1
dictProp = {'REFERENCE': 'WGS84', 'Coordinate1': \
            {'size': width, 'startingValue':startLon, 'delta':deltaLon}, \
            'Coordinate2': {'size': length, 'startingValue': startLat,  'delta':deltaLat}, \
                'FILE_NAME': 'stitched.dem'}
objdem.init(dictProp)
objdem.renderHdr()
os.system('chmod 777 *')
os.system('fixImageXml.py -i stitched.dem.xml -f')
os.system('chmod 777 *')



os.chdir(basedir)





#### get SRTM dem through dem.py #####
# DEM bbox (bbox contained within, but all integers (i.e., no decimals))
# dembbox    = [61, 62, -152, -148] # SNWE 
# # SRTM DEM source (-s): 1 if USA, 3 if global (this one is coarser)
# demsource = '3'

# # change dir to dem dir
# os.chdir(demdir)

# # get dem command
# command =  'dem.py -a download -c -b ' + str(dembbox[0]) + ' ' + str(dembbox[1]) + ' ' + str(dembbox[2]) + ' ' + str(dembbox[3]) + ' -r -s ' + demsource 
# # print(command)
# # os.system(command)

# # stitch dem command
# command2 = 'dem.py -a stitch -b ' + str(dembbox[0]) + ' ' + str(dembbox[1]) + ' ' + str(dembbox[2]) + ' ' + str(dembbox[3]) + ' -r -s ' + demsource + ' -l -k -c'
# # print(command2)
# # os.system(command2)

# # fix dem xml
# command3 = 'fixImageXml.py -i ' + demnm + ' -f'
# # print(command3)
# # os.system(command3)

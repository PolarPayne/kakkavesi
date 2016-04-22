#!/usr/bin/python3

from PIL import Image # python3-pil
import numpy # python3-numpy
import os 
from osgeo import osr, gdal, gdalconst # python3-gdal
from geopy.distance import GreatCircleDistance as coord_dist # python3-geopy

GEOTIFF_DIR = 'IL sadedata 2015'

# The following method translates given latitude/longitude pairs into pixel locations on a given GEOTIF
# INPUTS: geotifAddr - The file location of the GEOTIF
#      latLonPairs - The decimal lat/lon pairings to be translated in the form [[lat1,lon1],[lat2,lon2]]
# OUTPUT: The pixel translation of the lat/lon pairings in the form [[x1,y1],[x2,y2]]
# NOTE:   This method does not take into account pixel size and assumes a high enough 
#	  image resolution for pixel size to be insignificant
def latLonToPixel(geotifAddr, latLonPairs):
	# Load the image dataset
	ds = gdal.Open(geotifAddr)
	# Get a geo-transform of the dataset
	gt = ds.GetGeoTransform()
	# Create a spatial reference object for the dataset
	srs = osr.SpatialReference()
	srs.ImportFromWkt(ds.GetProjection())
	# Set up the coordinate transformation object
	srsLatLong = srs.CloneGeogCS()
	ct = osr.CoordinateTransformation(srsLatLong,srs)
	# Go through all the point pairs and translate them to latitude/longitude pairings
	pixelPairs = []
	for point in latLonPairs:
		# Change the point locations into the GeoTransform space
		(point[1],point[0],holder) = ct.TransformPoint(point[1],point[0])
		# Translate the x and y coordinates into pixel values
		x = (point[1]-gt[0])/gt[1]
		y = (point[0]-gt[3])/gt[5]
		# Add the point to our return array
		pixelPairs.append([int(x),int(y)])
	return pixelPairs
# The following method translates given pixel locations into latitude/longitude locations on a given GEOTIF
# INPUTS: geotifAddr - The file location of the GEOTIF
#      pixelPairs - The pixel pairings to be translated in the form [[x1,y1],[x2,y2]]
# OUTPUT: The lat/lon translation of the pixel pairings in the form [[lat1,lon1],[lat2,lon2]]
# NOTE:   This method does not take into account pixel size and assumes a high enough 
#	  image resolution for pixel size to be insignificant
def pixelToLatLon(geotifAddr,pixelPairs):
	# Load the image dataset
	ds = gdal.Open(geotifAddr)
	# Get a geo-transform of the dataset
	gt = ds.GetGeoTransform()
	# Create a spatial reference object for the dataset
	srs = osr.SpatialReference()
	srs.ImportFromWkt(ds.GetProjection())
	# Set up the coordinate transformation object
	srsLatLong = srs.CloneGeogCS()
	ct = osr.CoordinateTransformation(srs,srsLatLong)
	# Go through all the point pairs and translate them to pixel pairings
	latLonPairs = []
	for point in pixelPairs:
		# Translate the pixel pairs into untranslated points
		ulon = point[0]*gt[1]+gt[0]
		ulat = point[1]*gt[5]+gt[3]
		# Transform the points to the space
		(lon,lat,holder) = ct.TransformPoint(ulon,ulat)
		# Add the point to our return array
		latLonPairs.append([lat,lon])
 
	return latLonPairs

def enumfiles(dpath):
	for path, subdirs, files in os.walk(dpath):
	  for name in files:
	    yield os.path.join(path, name)
	return

cumulative_values = None

avg = None

maxsum = 0
maxweek = None

files = list(enumfiles(GEOTIFF_DIR))
N = len(files)

src = gdal.Open(files[0], gdalconst.GA_ReadOnly)
W, H = Image.open(files[0]).size

topleftc = pixelToLatLon(files[0], [[0,0]])
toprightc = pixelToLatLon(files[0], [[W,0]])
botrightc = pixelToLatLon(files[0], [[W,H]])

print("geotiff dimensions: %dx%d" % (W, H))
print("area width:", coord_dist(topleftc, toprightc))
print("area height:",coord_dist(toprightc, botrightc))

N = 1000
i = 0

for filepath in files:
	im = Image.open(filepath)
	imarray = numpy.array(im)	
	if avg == None: avg = imarray / N
	else: avg = avg + imarray / N
	#s = numpy.sum(imarray)
	#if s >= maxsum:
	#	maxweek	= imarray
	#	maxsum = s
	i += 1
	if i > N: break

avg = numpy.multiply(avg, 255.0/4.0);
avg=numpy.array(numpy.round(avg),dtype=numpy.uint8)

# show average of first N radar images
res = Image.fromarray(avg)
res.show();
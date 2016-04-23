#!/usr/bin/python3

from PIL import Image, ImageDraw # python3-pil
import numpy # python3-numpy
import os 
import shapefile # python3-pyshp
from osgeo import osr, gdal, gdalconst # python3-gdal
from geopy.distance import GreatCircleDistance as coord_dist # python3-geopy

from helpers import *

GEOTIFF_DIR = '../hackathon/IL sadedata 2015'
SHAPEFILE_DIR = '../hackathon/Pumppaamoalue-shape'

myshp = open(os.path.join(SHAPEFILE_DIR,"Alue.shp"), "rb")
mydbf = open(os.path.join(SHAPEFILE_DIR,"Alue.dbf"), "rb")
r = shapefile.Reader(shp=myshp, dbf=mydbf)
shapes = r.shapes()

shapeCoords = []

for s in shapes:
	shapeCoords.append([[pt[1]/100000, pt[0]/1000000] for pt in s.points])

print([shapeCoords[0][0]])

cumulative_values = None

avg = None

maxsum = 0
maxweek = None

files = list(enumfiles(GEOTIFF_DIR))
N = len(files)

src = gdal.Open(files[0], gdalconst.GA_ReadOnly)
W, H = Image.open(files[0]).size

topleftc = pixelToLatLon(files[0], [[0, 0]])
toprightc = pixelToLatLon(files[0], [[W, 0]])
botrightc = pixelToLatLon(files[0], [[W, H]])

print(topleftc)
print(botrightc)

print("geotiff dimensions: %dx%d" % (W, H))
print("area width:", coord_dist(topleftc, toprightc))
print("area height:", coord_dist(toprightc, botrightc))

N = 100
i = 0

for filepath in files:
    im = Image.open(filepath)
    imarray = numpy.array(im)
    if avg == None:
        avg = imarray / N
    else:
        avg = avg + imarray / N
    # s = numpy.sum(imarray)
    # if s >= maxsum:
    #	maxweek	= imarray
    #	maxsum = s
    i += 1
    if i > N: break

avg = numpy.multiply(avg, 255.0 / 4.0);
avg = numpy.array(numpy.round(avg), dtype=numpy.uint8)

# show average of first N radar images
res = Image.fromarray(avg)
res.show()


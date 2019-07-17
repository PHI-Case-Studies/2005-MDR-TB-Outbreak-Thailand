'''
GPS displacement process Python Script
@author: bcollins, Blue Raster, LLC
'''
from __future__ import division
import os
import sys
import random
import math
import arcpy
import traceback

class Displacer(object):
 '''
 Displaces a point location while preserving its location
 inside a given polygon
 '''

 def __init__(self):
     pass

 def displacePoint(self, x, y, maxDistance=5000):
     '''
     calculates new point up to a given distance away
     from original point. All values should be provided
     in meters

     point = (x,y)
     '''
     #The number pi
     PI = 3.14159267

     #Generate a random angle between 0 and 360
     angle_degree = random.randint(0, 360)
     #Convert the random angle from degrees to radians
     angle_radian = (angle_degree) * (PI/180)

     #Generate a random distance by multiplying the max distance by a random number between 0 and 1
     distance = random.random() * maxDistance

     #Generate the offset by applying trig formulas (law of cosines) using the distance as the
     # hypotenuse solving for the other sides

     xOffset = math.sin(angle_radian) * distance
     yOffset = math.cos(angle_radian) * distance 
     # if(angle_degree > 90 and angle_degree <= 270): xOffset *= -1
     # if(angle_degree > 180): yOffset *= -1

     #Add the offset to the orginal coordinate (in meters)
     new_x = x + xOffset
     new_y = y + yOffset

     return (new_x, new_y)

class GeometryHelpers(object):
 import arcpy
 import math

 def __init__(self):
     pass

 def getCoordinateUnits(self, feature_class):
     sr = arcpy.Describe(feature_class).spatialReference
     units = [sr.type, sr.name, sr.linearUnitName, sr.angularUnitName]
     return units

 def XYToPointGeometry(self, x, y, spatialReference):
     point = arcpy.Point(x, y)
     ptGeometry = arcpy.PointGeometry(point, spatialReference)
     return ptGeometry
    
 def degreesToMeters(self, xLong, yLat):
     #Convert decimal degrees to meters
     #A fixed conversion factor from degrees to radians
     DEG_TO_RAD = 0.017453292519943296
     #The number pi
     PI = 3.14159267
     #The earth's radius in meters
     EARTH_RADIUS = 6378137

     #This function will provide wrapping around the world, but only to half way back around.
     #This assertions protect against wacky coordinates
     assert (xLong < 360 and xLong > -360), 'longitude outside of wrapping bounds'
     assert (yLat < 180 and yLat > -180), 'latitude outside of wrapping bounds' 

     #Wrap around values if necessary
     if(yLat <= -90): yLat = yLat % 90
     if(yLat >= 90): yLat = (yLat % 90) - 90
     if(xLong <= -180): xLong = xLong % 180
     if(xLong >= 180): xLong = (xLong % 180) - 180 
     #The y formula uses yLat as a scalor to correct for differences in the number of meters in a degree of latitude across the earth
     y = EARTH_RADIUS * math.log(math.tan(((yLat * DEG_TO_RAD) + (PI / 2))/2))
     x = EARTH_RADIUS * (xLong * DEG_TO_RAD)

     return (x, y);

 #Convert meters to decimal degrees
 def metersToDegrees(self, xLong, yLat):
     #A fixed conversion factor from radians to degrees
     RAD_TO_DEG = 57.295779513082322
     #The number pi
     PI = 3.14159267
     #The earth's radius in meters
     EARTH_RADIUS = 6378137

     #Convert meters to decimal degrees
     lat = RAD_TO_DEG * ((2 * math.atan(math.exp(yLat / EARTH_RADIUS))) - (PI/2));
     lon = RAD_TO_DEG * (xLong / EARTH_RADIUS);

     #This function will provide wrapping around the world, but only to half way back around.
     #This assertions protect against wacky coordinates
     assert (lon < 360 and lon > -360), 'longitude outside of wrapping bounds'
     assert (lat < 180 and lat > -180), 'latitude outside of wrapping bounds'

     #Wrap around values if necessary
     if(lat<=-90): lat = lat % 90
     if(lat>=90): lat = (lat % 90) - 90
     if(lon<=-180): lon = lon % 180
     if(lon>=180): lon = (lon % 180) - 180

     return (lon, lat)

 def isGeographicProjection(self, feature_class):
     feature_class_description = arcpy.Describe(feature_class)
     proj_type = feature_class_description.spatialReference.type
     return (proj_type == 'Geographic')

 def validateGeometries(self, point_feature_class, polygon_feature_class):
     point_description = arcpy.Describe(point_feature_class)
     polygon_description = arcpy.Describe(polygon_feature_class)

     point_sr = point_description.spatialReference.name
     polygon_sr = polygon_description.spatialReference.name

     assert (point_sr == polygon_sr), 'Point and Polygon Spatial Reference Mismatch'

 def relatePointsToPolygons(self, point_feature_class, polygon_feature_class): 

     '''
     Input a point and polygon feature class and a receive a dictionary of which points are in which
    polygons
     '''
     returnDict = { }
     point_rows = arcpy.SearchCursor(point_feature_class)

     for p in point_rows:
         ppoint = p.getValue('Shape')
         polygon_rows = arcpy.SearchCursor(polygon_feature_class)
     for q in polygon_rows:
         poly = q.getValue('Shape')
     if(ppoint.within(poly)):
         returnDict[p] = poly
     del polygon_rows
     del point_rows

     return returnDict

 def createTimestamp(self):
     '''creates a timestamp which can be used to create a unique name.'''
     from time import localtime, strftime
     l = localtime()
     return strftime("%Y-%m-%d_%H_%M", l)

if __name__ == '__main__':
 try:
     #Helper Classes =====================================================================================
     oDisplacer = Displacer()
     oGeometryHelpers = GeometryHelpers()

     #Input Parameters =====================================================================================
     POINTS_PATH = arcpy.GetParameterAsText(0)
     POLYGON_PATH = arcpy.GetParameterAsText(1)
     MAX_DISTANCE = int(arcpy.GetParameterAsText(2))
     UPDATE_LAT_LON_MODE = arcpy.GetParameterAsText(3)
     LAT_FIELD = arcpy.GetParameterAsText(4)
     LON_FIELD = arcpy.GetParameterAsText(5)
     URBAN_RURAL_MODE = arcpy.GetParameterAsText(6)
     URBAN_RURAL_FIELD = arcpy.GetParameterAsText(7)
     URBAN_VALUE = arcpy.GetParameterAsText(8)
     RURAL_VALUE = arcpy.GetParameterAsText(9)
     OUTPUT_DATASET = arcpy.GetParameterAsText(10)
     REPORT_LOCATION = arcpy.GetParameterAsText(11) 
     #Setup Basic Report =====================================================================================
     REPORT_NAME = '_'.join(['Point_Displacement_Report', oGeometryHelpers.createTimestamp() +
    '.txt'])
     REPORT_FULL_PATH = os.path.join(REPORT_LOCATION, REPORT_NAME)
     report = open(REPORT_FULL_PATH, 'w')
     report.write(REPORT_NAME + '\n\n')
     report.write('Input Parameters: \n\n')
     report.write('POINTS INPUT PATH: %s \n' % POINTS_PATH)
     report.write('POLYGON INPUT PATH: %s \n' % POLYGON_PATH)
     report.write('MAX_DISTANCE: %i \n' % MAX_DISTANCE)
     report.write('URBAN_RURAL_MODE: %s \n' % URBAN_RURAL_MODE)
     report.write('URBAN_RURAL_FIELD: %s \n' % URBAN_RURAL_FIELD)
     report.write('URBAN_VALUE: %s \n' % URBAN_VALUE)
     report.write('RURAL_VALUE: %s \n' % RURAL_VALUE)
     report.write('OUTPUT_DATASET: %s \n\n' % OUTPUT_DATASET)

     report.write('TOOL MESSAGES: \n\n')

     arcpy.AddMessage('Report Location: %s' % REPORT_FULL_PATH)

     #GET INFORMATION ON POINTS LAYER =========================================================================
     point_description = arcpy.Describe(POINTS_PATH)
     point_shapefield = point_description.shapeFieldName
     point_fields = arcpy.ListFields(POINTS_PATH)
     point_field_dict = dict([(f.name, f.type) for f in point_fields])
     point_count = arcpy.GetCount_management(POINTS_PATH).getOutput(0)
     point_sr = point_description.spatialReference

     #GET INFORMATION ON POLYGON LAYER ========================================================================
     polygon_description = arcpy.Describe(POLYGON_PATH)
     polygon_shapefield = polygon_description.shapeFieldName
     polygon_fields = arcpy.ListFields(POLYGON_PATH)
     polygon_count = arcpy.GetCount_management(POINTS_PATH).getOutput(0)
     polygon_sr = polygon_description.spatialReference

     WORKSPACE = os.path.split(POINTS_PATH)[0]
     OUTPUT_WORKSPACE = os.path.split(OUTPUT_DATASET)[0]

     #Assert Statement to validate inputs=====================================================================
     assert arcpy.Exists(POINTS_PATH), 'Point Feature Class does not appear exist'
     assert arcpy.Exists(POLYGON_PATH), 'Polygon Feature Class does not appear exist'
     assert point_description.shapeType == 'Point', 'Point layer does not appear to be a Point layer'
     assert polygon_description.shapeType == 'Polygon', 'Polygon layer does not appear to be a Polygon layer' 
     assert point_count > 0, 'Dude...there are not any points in this file'
     assert os.path.exists(OUTPUT_WORKSPACE), 'Output Workspace does not appear to exist'
     assert oGeometryHelpers.isGeographicProjection(POINTS_PATH), 'Points file not in geographic projection'
     assert oGeometryHelpers.isGeographicProjection(POLYGON_PATH), 'Polygon file not in geographic projection'

     arcpy.env.workspace = WORKSPACE
     arcpy.env.overwriteOutput = True

     '''
     Many of the point datasets imported from excel contain Lat/Long fields
     which are static attributes. We want these fields to be updated to the new
     lat/long after the point is displaced. The script writes to these fields
     later on in the 'while' loop, but the code immediately below is used to make
     sure the fields supplied in the tool dialog actually exist.
     '''
     if(UPDATE_LAT_LON_MODE.lower() == 'true' or UPDATE_LAT_LON_MODE == '1'):
         UPDATE_LAT_LON_MODE = True
     assert (LAT_FIELD in point_field_dict.keys()), LAT_FIELD + ' not in point feature class fields'
     assert (LON_FIELD in point_field_dict.keys()), LON_FIELD + ' not in point feature class fields'
     assert (point_field_dict[LAT_FIELD] != 'String'), LAT_FIELD + ' appears to be a String field but should be a Double'
     assert (point_field_dict[LON_FIELD] != 'String'), LON_FIELD + ' appears to be a String field but should be a Double'

else:
     UPDATE_LAT_LON_MODE = False

 #Figure out which Tool Mode we are in (URBAN_RURAL_MODE true/false) ======================================
 if(URBAN_RURAL_MODE.lower() == 'true' or URBAN_RURAL_MODE == '1'):
 mode_name = ' Urban / Rural Mode'
 URBAN_RURAL_MODE = True
 else:
 mode_name = ' Maximum Displacement = ' + str(MAX_DISTANCE) + 'm'
 URBAN_RURAL_MODE = False

 if(URBAN_RURAL_MODE):
 assert (URBAN_RURAL_FIELD in point_field_dict.keys()), URBAN_RURAL_FIELD + ' not in point
feature class fields'
 point_search = arcpy.SearchCursor(POINTS_PATH)
 for p in point_search:
 locality = p.getValue(URBAN_RURAL_FIELD)
 assert (locality == URBAN_VALUE or locality == RURAL_VALUE), str(locality) + ' does not match
urban/rural values provided. Please check your attribute table and make sure all urban/rural values
match what was entered in the tool dialog.'
 del point_search 
 #Copy Feature Class as not to mess with the original data ================================================
 arcpy.CopyFeatures_management(POINTS_PATH, OUTPUT_DATASET)

 #MAIN BUSINESS LOGIC =====================================================================================
 point_rows = arcpy.UpdateCursor(OUTPUT_DATASET)
 arcpy.SetProgressor("step", "Displacing Points...", 0, int(point_count), 1)

 displaced_points = 0
 rural_displaced_points = 0

 #Loop through each of the points
 for p in point_rows:
 point_geom = p.getValue(point_shapefield)

 #Get Max Distance based on tool mode and current point attributes (urban vs. rural) ======================
 if(URBAN_RURAL_MODE):
 locality = p.getValue(URBAN_RURAL_FIELD)

 #Urban Point Displacement Logic
 if(locality == URBAN_VALUE):
 max_displace_distance = 2000

 #Rural Point Displacement Logic
 elif(locality == RURAL_VALUE):
 rural_displaced_points += 1
 max_displace_distance = (rural_displaced_points % 100 == 0) and 10000 or 5000

 #Use distance supplied by user if not in URBAN/RURAL MODE
 else:
 max_displace_distance = MAX_DISTANCE

 #Loop through each of the polygons
 polygon_rows = arcpy.SearchCursor(POLYGON_PATH)
 point_within_study_area = False
 for q in polygon_rows:
 poly_geom = q.getValue(polygon_shapefield)
 if(point_geom.within(poly_geom)):
 point_within_study_area = True

 new_point_within = False
 while(not new_point_within):
 ppoint = point_geom.firstPoint 
 #Convert from degrees to meters
 meter_x, meter_y = oGeometryHelpers.degreesToMeters(ppoint.X, ppoint.Y)

 #Run displacement function
 displaced_x, displaced_y = oDisplacer.displacePoint(meter_x, meter_y,
max_displace_distance)

 #Convert output back to degrees
 new_x, new_y = oGeometryHelpers.metersToDegrees(displaced_x, displaced_y)
 new_point = arcpy.Point(new_x, new_y)
 new_geometry = arcpy.PointGeometry(new_point, point_sr)

 #Check if point still remains inside the original polygon, if so
 #then this loop will end, if not the process begins again
 new_point_within = new_geometry.within(poly_geom)


 #Update Shape Field
 p.setValue(point_shapefield, new_geometry)

 #Update Static Lat/Lon fields
 if(UPDATE_LAT_LON_MODE):
 p.setValue(LAT_FIELD, new_y)
 p.setValue(LON_FIELD, new_x)

 point_rows.updateRow(p)
 displaced_points += 1
 arcpy.SetProgressorLabel('Displaced ' + str(displaced_points) + ' of ' + str(point_count) +
mode_name)
 arcpy.SetProgressorPosition()

 #Handle if point is not found within any of the study area polygons==================================
 if(not point_within_study_area):
 arcpy.AddWarning('Point Detected outside of study area. Please check report for more
details.')
 report.write('POINT OUTSIDE STUDY AREA: \n')
 for f in point_field_dict.keys():
 if(f != point_shapefield):
 v = p.getValue(f)
 report.write(' %s: %s \n' % (f, str(v)))
 report.write('\n\n')
 del polygon_rows
 del point_rows

 except AssertionError, e:
 report.write('AssertionError: %s' % e) 
 report.write('\n\n')
 del polygon_rows
 del point_rows

 except AssertionError, e:
 report.write('AssertionError: %s' % e) 
 
 
 
 
 

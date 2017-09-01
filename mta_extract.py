#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# mta_extract.py
# The purpose of this scripts is collect and process spatial data from the MTA
# GTFS using arcpy. This data includes:
#    * Subway Station Points
#    * Subway Route Lines
#    * Bus Stop Points
#    * Bus Route Lines
#
# C:\Python27\ArcGIS10.4\python.exe mta_extract.py
# ---------------------------------------------------------------------------
import os, json, csv, datetime, timeit, urllib2, shutil, zipfile, arcpy

title = '''

                 ___ ___  ______   ____
                |   |   ||      | /    |
                | _   _ ||      ||  o  |
                |  \_/  ||_|  |_||     |
                |   |   |  |  |  |  _  |
                |   |   |  |  |  |  |  |
                |___|___|  |__|  |__|__|

                   ___  __ __  ______  ____    ____    __ ______
                  /  _]|  |  ||      ||    \  /    |  /  ]      |
                 /  [_ |  |  ||      ||  D  )|  o  | /  /|      |
                |    _]|_   _||_|  |_||    / |     |/  / |_|  |_|
                |   [_ |     |  |  |  |    \ |  _  /   \_  |  |
                |     ||  |  |  |  |  |  .  \|  |  \     | |  |
                |_____||__|__|  |__|  |__|\_||__|__|\____| |__|

'''
root = os.path.abspath(os.path.curdir)
gdb = root + "\\tmp.gdb"
dir_gtfs = root + "\\ALL_GTFS"
stops = dir_gtfs + "\\MTA_Subway\\stops.txt"

wgs84 = "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]];-400 -400 1000000000;-100000 10000;-100000 10000;8.98315284119522E-09;0.001;0.001;IsHighPrecision"

gtfs = {
   "list":[
      {
         "name":"MTA_Subway",
         "url":"http://web.mta.info/developers/data/nyct/subway/google_transit.zip",
      },
      {
         "name":"MTA_Bus_Manhattan",
         "url":"http://web.mta.info/developers/data/nyct/bus/google_transit_manhattan.zip",
      },
      {
         "name":"MTA_Bus_Bronx",
         "url":"http://web.mta.info/developers/data/nyct/bus/google_transit_bronx.zip",
      },
      {
         "name":"MTA_Bus_Brooklyn",
         "url":"http://web.mta.info/developers/data/nyct/bus/google_transit_brooklyn.zip",
      },
      {
         "name":"MTA_Bus_Queens",
         "url":"http://web.mta.info/developers/data/nyct/bus/google_transit_queens.zip",
      },
      {
         "name":"MTA_Bus_Staten_Island",
         "url":"http://web.mta.info/developers/data/nyct/bus/google_transit_staten_island.zip",
      },
   ],
   "folders":[
      {"name":"ALL_GTFS"},
      {"name":"subway_stations"},
      {"name":"subway_routes"},
      {"name":"bus_stops"},
      {"name":"bus_lines"},
   ],}

overlapping = {
 '125': [40.666666, -73.666666],
 '222': [40.111111, -73.111111],
 '415': [40.768247, -73.981929],
 '710': [40.666666, -73.666666],
 '718': [40.111111, -73.111111],
 'A24': [40.666666, -73.666666],
 'A32': [40.111111, -73.111111],
 'D20': [40.666666, -73.666666],
 'G14': [40.111111, -73.111111],
 'M22': [40.666666, -73.666666],
 'R09': [40.111111, -73.111111],
}

def manage_directories(d):
    #creates or replaces drectories
    for i in d['folders']:
        if os.path.exists(i['name']):
            shutil.rmtree(root + '/' + i['name'])
            os.makedirs(i['name'])
        else:
            os.makedirs(i['name'])

    if os.path.exists(gdb):
        shutil.rmtree(gdb)
        arcpy.CreateFileGDB_management(root, "tmp.gdb")
    else:
        arcpy.CreateFileGDB_management(root, "tmp.gdb")

def get_gtfs(d):
    #used to over come proxy issue in the office
    proxy = urllib2.ProxyHandler({})
    opener = urllib2.build_opener(proxy)
    urllib2.install_opener(opener)

    #loop our list of gtfs we need to download
    for i in d['list']:
        f = urllib2.urlopen(i['url'])
        data = f.read()
        with open(i['name'] + ".zip", "wb") as code:
            code.write(data)
        #extracts zips to ALL-GTFS folders then removes the zip.
        with zipfile.ZipFile(root + '/' + i['name']+ '.zip', "r") as z:
            z.extractall(root + '/' + 'ALL_GTFS' + '/' + i['name'])

        print("    " + i['name'] + " : Downloaded and Unzipped")
        os.remove(i['name'] + ".zip")

def adjust_subway_text():
    with open(stops, 'r') as lines:
        stop_list = [l for l in lines]

    for i in stop_list:

        if i[:3] in overlapping:
            new_lat = overlapping[i[:3]][0]
            new_long = overlapping[i[:3]][1]

            old_lat = i.split(',')[4]
            old_long = i.split(',')[5]

            new_i = i.replace(old_lat, str(new_lat)).replace(old_long, str(new_long))
            stop_list[stop_list.index(i)] = new_i

    with open(r'C:\GitHub\Python\iridenyc_update\ALL_GTFS\MTA_Subway\stops_corrected.txt', 'w') as txt:
        for i in stop_list:
            txt.write(i)

def create_subway_stations():
    stops_txt = root + "\\ALL_GTFS\\MTA_Subway\\stops_corrected.txt"
    stops_CopyRow = root + "\\tmp.gdb\\stops_CopyRow"
    stops = "stops"
    subway_stations = root + "\\subway_stations"
    subway_stations_shp = root +"\\subway_stations\\subway_stations.shp"

    arcpy.CopyRows_management(stops_txt, stops_CopyRow, "")
    arcpy.MakeXYEventLayer_management(stops_CopyRow, "stop_lon", "stop_lat", stops, wgs84, "")
    arcpy.FeatureClassToFeatureClass_conversion(stops, subway_stations ,"subway_stations.shp" ,"\"stop_id\" LIKE '%S' OR \"stop_id\" LIKE '%N'")
    print("    Subway Stations Created")

def create_subway_lines():
    line_txt = root + "\\ALL_GTFS\\MTA_Subway\\shapes.txt"
    line_CopyRow = root + "\\tmp.gdb\\line_CopyRow"
    line = "line"
    subway_line = root + "\\tmp.gdb"
    subway_line_ft = root + "\\tmp.gdb\\subway_routes"
    subway_line_shp = root + "\\subway_routes\\subway_routes.shp"

    arcpy.CopyRows_management(line_txt, line_CopyRow, "")
    arcpy.MakeXYEventLayer_management(line_CopyRow, "shape_pt_lon", "shape_pt_lat", line, wgs84, "")
    arcpy.FeatureClassToFeatureClass_conversion(line, subway_line ,"subway_routes", "")
    arcpy.PointsToLine_management(subway_line_ft, subway_line_shp, "shape_id", "shape_pt_sequence")
    print("    Subway Lines Created")

def create_bus_stops():
    w = os.path.abspath(os.path.expanduser(root + "\All_GTFS"))
    x = os.listdir(w)
    for i in x:
        if "MTA_Bus" in i:
            arcpy.CopyRows_management(w + "\\" + i + "\\stops.txt", root + "\\tmp.gdb\\" + i +"_s", "")
            arcpy.MakeXYEventLayer_management(root + "\\tmp.gdb\\" + i +"_s", "stop_lon", "stop_lat", i +"_s" , wgs84, "")
            arcpy.FeatureClassToFeatureClass_conversion(i +"_s" , root + "\\tmp.gdb" , i + "_stops", "")

    y = os.path.abspath(os.path.expanduser(root + "\\tmp.gdb"))
    z  = os.path.abspath(os.path.expanduser(root + "\\bus_stops"))
    arcpy.Merge_management([  y + "\MTA_Bus_Bronx_stops", y + "\MTA_Bus_Brooklyn_stops", y + "\MTA_Bus_Manhattan_stops", y + "\MTA_Bus_Queens_stops", y + "\MTA_Bus_Staten_Island_stops",], y + "\\bus_stops")
    arcpy.FeatureClassToShapefile_conversion([y + "\\bus_stops"], z)
    print("    Bus Stops Created")

def create_bus_lines():
  w = os.path.abspath(os.path.expanduser(root + "\All_GTFS"))
  x = os.listdir(w)
  for i in x:
      if "MTA_Bus" in i:
          arcpy.CopyRows_management(w + "\\" + i + "\\shapes.txt", root + "\\tmp.gdb\\" + i +"_l", "")
          arcpy.MakeXYEventLayer_management(root + "\\tmp.gdb\\" + i +"_l", "shape_pt_lon", "shape_pt_lat", i +"_l" , wgs84, "")
          arcpy.FeatureClassToFeatureClass_conversion(i +"_l" , root + "\\tmp.gdb" , i + "_lines", "")

  y = os.path.abspath(os.path.expanduser(root + "\\tmp.gdb"))
  z  = os.path.abspath(os.path.expanduser(root + "\\bus_lines"))
  arcpy.Merge_management([  y + "\MTA_Bus_Bronx_lines", y + "\MTA_Bus_Brooklyn_lines", y + "\MTA_Bus_Manhattan_lines", y + "\MTA_Bus_Queens_lines", y + "\MTA_Bus_Staten_Island_lines",], y + "\\bus_lines")
  arcpy.PointsToLine_management(y + "\\bus_lines", z + "\\bus_lines.shp", "shape_id", "shape_pt_sequence")
  print("    Bus Lines Created")

def main():
    start = timeit.default_timer()
    print(title)
    manage_directories(gtfs)
    get_gtfs(gtfs)
    adjust_subway_text()
    create_subway_stations()
    create_subway_lines()
    create_bus_stops()
    create_bus_lines()
    stop = timeit.default_timer()
    print("    Total Run Time : " +  str(stop - start) + " seconds")

if __name__ == '__main__':
    main()

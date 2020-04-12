# -*- coding: utf-8 -*-
"""
Created on Sun Apr 12 17:40:14 2020

Distributed under GNU GPLv3
@author: Chris Stuart <chrisistuart@gmail.com>

Methods for accessing high resolution sea surface temperature data through
publicly available NetCDF4 OpenDAP interfaces. Data comes from two datasets:
    
GHRSST Level 4 OSPO Global Foundation Sea Surface Temperature Analysis (GDS
version 2)
    https://podaac.jpl.nasa.gov/dataset/Geo_Polar_Blended-OSPO-L4-GLOB-v1.0
    
GHRSST Level 4 OSPO Global Nighttime Foundation Sea Surface Temperature
Analysis (GDS version 2)
    https://podaac.jpl.nasa.gov/dataset/Geo_Polar_Blended_Night-OSPO-L4-GLOB-v1.0
    
This data is available from 2014-06-02 until present (2020-04-12 at writing)
with some gaps. Temperatures are an average for the day.
"""

import netCDF4
import datetime

def sst_url(date, source_string=None):
    '''Generate the URL for the podaac opendap Geo_Polar_Blended netcdf4 dataset for a particular day'''
    # First of all, we extract the day, month and year
    day_of_month = date.day
    month = date.month
    year = date.year

    # Then we also get the day of the year
    day_of_year = 1+(date.date() - datetime.date(year,1,1)).days

    # We allow the user to specify a different url, but if
    # dont then we provide the default url source string
    if source_string is None:
        source_string = "https://podaac-opendap.jpl.nasa.gov/opendap/hyrax/allData/ghrsst/data/GDS2/L4/GLOB/OSPO/Geo_Polar_Blended/v1/%04d/%03d/%04d%02d%02d000000-OSPO-L4_GHRSST-SSTfnd-Geo_Polar_Blended-GLOB-v02.0-fv01.0.nc"

    # Finally we return the source string but with all the
    # expected pieces slotted into it
    return source_string % (year, day_of_year, year, month, day_of_month)

def latitude_index(lat, lat_min=-90, lat_max=90, index_length=3600):
    '''Calculate the closest index (6km boxes) for latitude'''
    return int(0.5 + (lat - lat_min)/(lat_max - lat_min)*(index_length-1))

def longitude_index(lon, lon_min=-180, lon_max=180, index_length=7200):
    '''Calculate the closest index (6km boxes) for longitude'''
    return int(0.5 + (lon - lon_min)/(lon_max - lon_min)*(index_length-1))

def get_sst_data(date, lat=None, lon=None, base_url=None, gz=False, night=None):
    '''Find the appropriate URL for this date, latitude and longitude and
    return a netCDF4.Dataset object connected to it. It will try a URL without
    the .gz at the end first, which is the more recent format. If that fails,
    it will try the same URL but with .gz added. If that fails, it will print
    an error. If no latitude or longitude are provided, then the full dataset
    will be returned instead.
    '''
    if night is not None and base_url is not None:
        raise Exception("It is not permitted to provide both arguments 'night' and 'base_url'")
        
    if base_url is None:
        if night:
            base_url = "https://podaac-opendap.jpl.nasa.gov/opendap/allData/ghrsst/data/GDS2/L4/GLOB/OSPO/Geo_Polar_Blended_Night/v1/%04d/%03d/%04d%02d%02d000000-OSPO-L4_GHRSST-SSTfnd-Geo_Polar_Blended_Night-GLOB-v02.0-fv01.0.nc"
        else:
            base_url = "https://podaac-opendap.jpl.nasa.gov/opendap/hyrax/allData/ghrsst/data/GDS2/L4/GLOB/OSPO/Geo_Polar_Blended/v1/%04d/%03d/%04d%02d%02d000000-OSPO-L4_GHRSST-SSTfnd-Geo_Polar_Blended-GLOB-v02.0-fv01.0.nc"
        
    try:
        if lat is None or lon is None:
            opendap_url = base_url
        else:
            lat_idx = latitude_index(lat)
            lon_idx = longitude_index(lon)
            opendap_url = base_url + \
                          "?analysed_sst[0:1:0][%d:1:%d][%d:1:%d],lat[%d:1:%d],lon[%d:1:%d]" % (
                              lat_idx,
                              lat_idx,
                              lon_idx,
                              lon_idx,
                              lat_idx,
                              lat_idx, 
                              lon_idx, 
                              lon_idx,
                          )
        #At this point, opendap_url specifies the latitude and longitude
        #(or doesn't, if that's what was requested), and the sst_url function
        #will insert the date to the URL.
        full_url = sst_url(date, source_string=opendap_url)
        #The URL is now complete and we should open the dataset ready to return
        sst_data = netCDF4.Dataset(full_url)
    except OSError as e:
        #If there was a problem, first print the error to the console
        print(str(e))
        #Then, if this didn't already have .gz in the URL then try just 
        #looking for the data with .gz in the URL
        if not gz:
            sst_data = get_sst_data(date, lat=lat, lon=lon, base_url=base_url+".gz", gz=True)
        else:
            #But if we already tried that, then we don't know what to do with
            #this error so we raise it further
            raise
    return sst_data

# -*- coding: utf-8 -*-
"""
Created on Sun Apr 12 17:40:14 2020

Distributed under GNU GPLv3
@author: Chris Stuart <chrisistuart@gmail.com>

Methods for accessing high resolution sea surface temperature data through
publicly available NetCDF4 OpenDAP interfaces. Data comes from three datasets:
    
GHRSST Level 4 OSPO Global Foundation Sea Surface Temperature Analysis (GDS
version 2)
    https://podaac.jpl.nasa.gov/dataset/Geo_Polar_Blended-OSPO-L4-GLOB-v1.0
    
GHRSST Level 4 OSPO Global Nighttime Foundation Sea Surface Temperature
Analysis (GDS version 2)
    https://podaac.jpl.nasa.gov/dataset/Geo_Polar_Blended_Night-OSPO-L4-GLOB-v1.0
    
This data is available from 2014-06-02 until present (2020-08-19 at writing)
with some gaps. Temperatures are an average for the day.

GHRSST Level 4 CMC 0.2deg Global Sea Surface Temperature Analysis (version 2)
    https://podaac.jpl.nasa.gov/dataset/CMC0.2deg-CMC-L4-GLOB-v2.0
    
This data is available from 1990-09-01 until 2017-03-17. Temperatures are
based on the 24 hours preceeding each midday.
"""

import netCDF4
import datetime

class GHRSSTNetCDFSource:
    '''Objects describing one PODAAC OpenDAP NetCDF4 dataset providing
    global high resolution sea surface temperature analyses.
    '''
    
    def __init__(self, sst_variable_name='analysed_sst', lat_min=-90, lat_max=90, lat_idx_len=3600, lon_min=-180, lon_max=180, lon_idx_len=7200):
        '''Set up parameters common to all of these datasets'''
        self.lat_min = float(lat_min)
        self.lat_max = float(lat_max)
        self.lat_idx_len = int(lat_idx_len)
        self.lon_min = float(lon_min)
        self.lon_max = float(lon_max)
        self.lon_idx_len = int(lon_idx_len)
        self.sst_variable_name = str(sst_variable_name)
        
    def get_csv_file_name(self):
        '''Return a short string which may be used in filenames to identify from which source the data was extracted'''
        raise NotImplementedError()

    def latitude_index(self, lat):
        '''Calculate the closest index for latitude'''
        return int(0.5 + (lat - self.lat_min)/(self.lat_max - self.lat_min)*(self.lat_idx_len-1))
    
    def longitude_index(self, lon):
        '''Calculate the closest index (6km boxes) for longitude'''
        return int(0.5 + (lon - self.lon_min)/(self.lon_max - self.lon_min)*(self.lon_idx_len-1))
    
    def date_uses_gz(self, date):
        '''Return whether the data on this date is stored in a gz compressed
        file which is not included in its base URL'''
        return False
    
    def get_sst_url(self, date, lat, lon):
        '''Generate the URL for this OpenDAP NetCDF4 dataset for a particular
        day, latitude and longitude'''
        # First of all, we extract the day, month and year
        day_of_month = date.day
        month = date.month
        year = date.year
    
        # Then we also get the day of the year
        day_of_year = 1+(date.date() - datetime.date(year,1,1)).days
    
        if self.date_uses_gz(date):
            source_string = self.get_base_url()+'.gz'
        else:
            source_string = self.get_base_url()
        
        # We place this info into the url
        date_url = source_string % (year, day_of_year, year, month, day_of_month)
        
        # Finally we add the request for the specific variable we want at the latitude and longitude we want, if any
        specific_url = date_url
        if lat is None or lon is None:
            if not (lat is None and lon is None):
                raise ValueError('Both or neither of lat and lon must be specified.')
        else:
            lat_idx = self.latitude_index(lat)
            lon_idx = self.longitude_index(lon)
            specific_url += \
                          "?%s[0:1:0][%d:1:%d][%d:1:%d],lat[%d:1:%d],lon[%d:1:%d]" % (
                              self.sst_variable_name,
                              lat_idx,
                              lat_idx,
                              lon_idx,
                              lon_idx,
                              lat_idx,
                              lat_idx, 
                              lon_idx, 
                              lon_idx,
                          )
        return specific_url
    
    def get_sst_data(self, date, lat=None, lon=None):
        '''Find the appropriate URL for this date, latitude and longitude and
        return a netCDF4.Dataset object connected to it. If no latitude or
        longitude are provided, then the full dataset for that date will be
        returned instead.
        '''
        # Get the URL with optional longitude and latitude and with the 
        # specified date inserted.
        full_url = self.get_sst_url(date, lat, lon)
        print(full_url)
        # Open the dataset ready to return
        sst_data = netCDF4.Dataset(full_url)
        return sst_data

class GeoPolarBlended(GHRSSTNetCDFSource):
    def get_base_url(self):
        return "https://podaac-opendap.jpl.nasa.gov/opendap/hyrax/allData/ghrsst/data/GDS2/L4/GLOB/OSPO/Geo_Polar_Blended/v1/%04d/%03d/%04d%02d%02d000000-OSPO-L4_GHRSST-SSTfnd-Geo_Polar_Blended-GLOB-v02.0-fv01.0.nc"
    def date_uses_gz(self, date):
        return date.date() < datetime.date(2016,2,11)
    def get_csv_file_name(self):
        return 'gpb'
    
class GeoPolarBlendedNight(GeoPolarBlended):
    def get_base_url(self):
        return "https://podaac-opendap.jpl.nasa.gov/opendap/allData/ghrsst/data/GDS2/L4/GLOB/OSPO/Geo_Polar_Blended_Night/v1/%04d/%03d/%04d%02d%02d000000-OSPO-L4_GHRSST-SSTfnd-Geo_Polar_Blended_Night-GLOB-v02.0-fv01.0.nc"
    def get_csv_file_name(self):
        return 'gpb_night'

class CMCZeroPointTwoDeg(GHRSSTNetCDFSource):
    def __init__(self):
        super().__init__(lat_idx_len=901, lon_idx_len=1800, lon_max=179.800003)
    def get_base_url(self):
        return "https://podaac-opendap.jpl.nasa.gov/opendap/hyrax/allData/ghrsst/data/GDS2/L4/GLOB/CMC/CMC0.2deg/v2/%04d/%03d/%04d%02d%02d120000-CMC-L4_GHRSST-SSTfnd-CMC0.2deg-GLOB-v02.0-fv02.0.nc"
    def get_csv_file_name(self):
        return 'cmc0.2'
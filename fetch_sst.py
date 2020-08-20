# -*- coding: utf-8 -*-
"""
Created on Sun Apr 12 17:50:55 2020

Distributed under GNU GPLv3
@author: Chris Stuart <chrisistuart@gmail.com>

"""

import ghrsst
import datetime

def fetch_sst_and_store_as_csv(sst_source, start_date, end_date, this_lat, this_lon):
    '''Method to read from a date range at a specific latitude and longitude
    for either the combined or the night-only datasets for SST.
    '''
    #We are going to open a file to store data in, first we need a name for it
    filename_base = sst_source.get_csv_file_name() + "_from_%04d%02d%02d_to_%04d%02d%02d_at_%.3fN_%.3fE.csv"
        
    filename = filename_base % (
                   start_date.year, 
                   start_date.month, 
                   start_date.day, 
                   end_date.year, 
                   end_date.month, 
                   end_date.day, 
                   this_lat, 
                   this_lon
               )
    
    #Now we open the file to write, and buffer only one line at a time because
    #we like to peek at the data as it is collected
    with open(filename, "w", buffering=1) as f:
        #Write the CSV header row
        f.write("year,month,day,latitude,longitude,analysed_sst\n")
        
        #Create a list of numbers starting at 0 with as many items as there are
        #going to be dates in our date_range
        days_range = range((end_date-start_date).days+1)
        for d in days_range:
            #Find the day we are looking at in this round of the loop, and
            #print it to the console so the user can see the progress
            this_day = start_date + datetime.timedelta(days=d)
            print(this_day.strftime("%Y-%m-%d"))
            
            #Now try to get data, and if it fails print a message that there
            #was no data
            try:
                this_data = sst_source.get_sst_data(this_day, lat=this_lat, lon=this_lon)
                
                #If the line above didn't fail then we have data! Extract the
                #sst from the netCDF4.Dataset object and print it to console
                this_sst = this_data.variables["analysed_sst"][0][0][0]-273.15
                print(this_sst)
                
                #Then, write it into our .csv file
                f.write("%d,%d,%d,%.3f,%.3f,%.2f\n" % (
                    this_day.year,
                    this_day.month,
                    this_day.day,
                    this_data.variables["lat"][0],
                    this_data.variables["lon"][0],
                    this_sst,
                ))
                
                #Finally, close the netCDF4.Dataset object. It maintains a
                #connection to the server until you do this, and the server 
                #will (apparently, through experience) only allow 27
                #concurrent connections, so if you don't close() them as you
                #go the script will fail after 27 days.
                this_data.close()
                
            except OSError as e:
                print(e)
                print("no data")
                
    print("Finished writing to " + filename)

#Now we write the code that will run if we type 'python fetching_sst.py'
if __name__ == "__main__":

    #If this is run as a script from the command line, then it could accept
    #command line arguments to set the start and end date and the latitude and
    #longitude. To read command line arguments, use the argparse library.
    import argparse
    parser = argparse.ArgumentParser()
    
    #Specify what arguments you would expect, and give them help strings so
    #that a user can type "python fetching_sst.py -h" to learn how to use
    #our script. Also give default values in case they give no arguments or
    #only some arguments.
    parser.add_argument("-s", "--start_date", required=False, default="2014-06-02", help="The first date to collect SST for")
    parser.add_argument("-e", "--end_date", required=False, default=None, help="The last date to collect SST for")
    parser.add_argument("--latitude", required=False, default="42.575", help="The latitude (degrees north) to collect SST for")
    parser.add_argument("--longitude", required=False, default="141.675", help="The longitude (degrees east) to collect SST for")
    parser.add_argument("--source", required=False, default="GeoPolarBlended", help="Set which dataset to use: GeoPolarBlended (default), GeoPolarBlendedNight or CMCZeroPointTwoDeg")
    
    #Then, run the parser and store the result in args.
    args = parser.parse_args()
    
    #The arguments are strings, we have to convert the dates into datetime
    #objects, which we'll use the dateutil package for
    from dateutil import parser as dateutilparser
    
    #Get the first date to gather data for
    start_date = dateutilparser.parse(args.start_date)
    #And the last date, which will be yesterday if nothing was provided
    if args.end_date is None:
        end_date = datetime.datetime.today() - datetime.timedelta(days=1)
    else:
        end_date = dateutilparser.parse(args.end_date)
        
    #The arguments are strings, we have to convert the location into floats
    #Get the latitude (deg N) as a float
    this_lat = float(args.latitude)
    #Get the longitude (deg E) as a float
    this_lon = float(args.longitude)
    
    #Finally, we'll get an instance of our chosen source of SST data
    sst_source = getattr(ghrsst, args.source)()
    
    #We have all our parameters, let's go...
    fetch_sst_and_store_as_csv(sst_source, start_date, end_date, this_lat, this_lon)
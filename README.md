# ghrsst
A Python package for extracting data from Geo_Polar_Blended-OSPO-L4-GLOB-v1.0,
Geo_Polar_Blended_Night-OSPO-L4-GLOB-v1.0 and CMC0.2deg-CMC-L4-GLOB-v2.0

Quickstart
----------

This package is best used with an Anaconda environment. From your Anaconda
prompt and in the cloned directory type:

```
$ conda env create -f environment.yaml
$ conda activate sst3-7
```

From this point, you can run the command-line script or start incorporating
the module into your scripts.

Command line examples
---------------------

* See the usage:
```
$ python fetch_sst.py --help
```

* Get SST at Theddlethorpe beach since April Fool's Day 2020:
```
$ python fetch_sst.py --start_date 2020-04-01 --lat 53.360449 --lon 0.258434
```

* Get night-time SST in Tomakomai bay in 2018:
```
$ python fetch_sst.py --start_date 2018-01-01 --end_date 2018-12-31 --source CMCZeroPointTwoDeg
```

Installation
------------

You may wish to install the module so that it can be accessed by scripts in
other directories.

From the clone directory, you can type

```
$ pip install .
```

However, be wary of combining use of `pip` and `conda`. Try to only ever use
`pip` once your Anaconda environment is stable. This package has declared no
dependencies, so it should not break your Anaconda environment. Maybe.

Details on the data
-------------------

This package provides a module for accessing high resolution sea surface
temperature data through publicly available NetCDF4 OpenDAP interfaces. Data
comes from two datasets:
    
* GHRSST Level 4 OSPO Global Foundation Sea Surface Temperature Analysis (GDS
version 2)
    * https://podaac.jpl.nasa.gov/dataset/Geo_Polar_Blended-OSPO-L4-GLOB-v1.0
    
* GHRSST Level 4 OSPO Global Nighttime Foundation Sea Surface Temperature
Analysis (GDS version 2)
    * https://podaac.jpl.nasa.gov/dataset/Geo_Polar_Blended_Night-OSPO-L4-GLOB-v1.0
    
This data is available from 2014-06-02 until present (2020-08-19 at writing)
with some gaps. Temperatures are given as an average for the 24 hours or for
the night-time.

* GHRSST Level 4 CMC 0.2deg Global Sea Surface Temperature Analysis (version 2)
    * https://podaac.jpl.nasa.gov/dataset/CMC0.2deg-CMC-L4-GLOB-v2.0
    
This data is available from 1990-09-01 until 2017-03-17. Temperatures are
based on the 24 hours preceeding each midday.
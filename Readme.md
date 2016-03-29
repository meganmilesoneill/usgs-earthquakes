# usgs-earthquakes

## summary

This project brings together earthquake event data with fault data to allow for fault-related earthquake data analysis.

## data
Earthquake data is imported from the USGS Earthquake Catalog.  The web service allows you to query summary data using search parameters such as starttime, endtime, and location.  There are also detailed product offerings such as focal mechanism, moment tensor, tectonic summary, and shakemap.

Currently, in order to retrieve detailed product offerings, it is necessary to make separate call to the web service for each earthquake event.

This library loads the summary data and product data into a PostgreSql database so that data analysis across detailed data such as focal mechanism is easier to perform.

This library also loads the fault line geographies according to the USGS Quaternary database.  This data is used to examine earthquake events in the context of fault lines to allow analysis of fault behavior.

**Earthquake Catalog:** http://earthquake.usgs.gov/fdsnws/event/1/

**Data Glossary:** http://earthquake.usgs.gov/earthquakes/feed/v1.0/glossary.php

**USGS Quaternary Data:**
http://earthquake.usgs.gov/hazards/qfaults/

*All data is provided courtesy of the U.S. Geological Survey.*

### Notes on data download decisions
USGS earthquake data comes in summary and detail formats.  The summary view does not include product data such as focal-mechanism and moment-tensor.  There are two methods for retrieving this data:
** Use the producttypes filter from USGS to return only those events that have the product data in question
** Download summary data, and make separate requests for each event that has the product data (the "types" property lists products available for a given event.)

Given that it may be of interest to see all records, I wanted to provide that option by using the second method.  The first method is also largely covered by another library provided by USGS: https://github.com/usgs/libcomcat

***Why PostgreSql instead of downloading to file?***
I tested an approach where I download the summary data into files broken down into monthly segments and then downloading each detail file as needed.  Early testing resulted in a directory with ~6K files, which caused issues in my editor and in Finder on MacOSX.  Given that a full download would likely create 20K-200K files, I abandoned this approach.

I also considered merging the detail data into a summary detail file, but this would result in large files, even if broken down into monthly files, and the merge process would be complex and error prone.

As a compromise, I opted to return to simply importing directly into a database with GIS support using SqlAlchemy.  If you are using another database supported by SqlAlchemy, you should be able to switch out the driver in the configuration file without encountering too many issues, but I have not yet tested this.

## Requirements
This library was built using the Anaconda Python distribution on Mac OSX (Yosemite 10.10).

* Python 3.5 (though it may work with Python 2.7)
* PostgreSql 9.5
* PostGIS
* GDAL
* psycopg2
* SqlAlchemy
* GeoAlchemy2
* numpy
* scipy
* Shapely

## Setup
*This section is not yet completed*
* Install PostgreSql database
* Install required packages
* download source
* update the configuration file (configuration.json)
* run unittests to ensure that setup was successful
* run load_all_data.py

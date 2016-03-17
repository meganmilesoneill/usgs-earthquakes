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

## Requirements
This library was built using the Anaconda Python distribution on Mac OSX (Yosemite 10.10).

* Python 3.5 (though it may work with Python 2.7)
* PostgreSql 9.5
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

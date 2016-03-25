from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from datasources import comcat, quaternary
from models import earthquakes
import configuration

def updateEarthquakeData(config):
	loader = comcat.ComcatLoader(config)
	loader.update(withNearestFaults = True)

def main():
	config = configuration.Configuration()
	updateEarthquakeData(config)

	print("update complete.")

if __name__ == "__main__":
	main()

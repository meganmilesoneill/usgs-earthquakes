from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from datasources import comcat, quaternary
from models import earthquakes
import configuration

def createDatabase(config):
	databaseUrl = '{0}://{1}/{2}'.format(config.database["provider"], config.database["server"], config.database["name"])

	engine = create_engine('postgres://localhost/postgres', echo=False)
	conn = engine.connect()
	conn.execute("COMMIT")
	conn.execute("DROP DATABASE IF EXISTS %s;" % config.database["name"])
	conn.execute("COMMIT")
	conn.execute("CREATE DATABASE %s;" % config.database["name"])
	conn.close()

	print("connecting to database")
	print("Database Url: %s" % databaseUrl)
	engine = create_engine(databaseUrl, echo=False)
	conn = engine.connect()
	conn.execute("COMMIT")
	conn.execute("CREATE EXTENSION postgis;")
	conn.close()

	print("creating earthquake tables")
	earthquakes.Fault.__table__.create(engine)

	# There is an issue with creating the GEOGRAPHY PostGIS type
	# using GeoAlchemy.  It does not allow the insertion of 3D points.
	# This is a work-around for now, as it seems to be an issue only with
	# the table create statement.
	earthquakes.Earthquake.__table__.create(engine)
	conn = engine.connect()
	conn.execute("COMMIT")
	conn.execute("ALTER TABLE earthquake DROP COLUMN geometry;")
	conn.execute("COMMIT")
	conn.execute("ALTER TABLE earthquake ADD COLUMN geometry GEOGRAPHY;")
	conn.execute("CREATE INDEX idx_earthquake_geometry ON earthquake USING GIST(geometry);")
	conn.close()

	earthquakes.EarthquakeFaultLink.__table__.create(engine)
	earthquakes.FocalMechanism.__table__.create(engine)
	earthquakes.MomentTensor.__table__.create(engine)

	print("Resetting last success date")
	cloader = comcat.ComcatLoader(config)
	cloader.reset()

def updateFaultData(config):
	print("Loading fault data.")
	qloader = quaternary.QuaternaryLoader(config)
	qloader.update()

def updateEarthquakeData(config):
	print("Loading earthquake data.")
	loader = comcat.ComcatLoader(config)
	loader.update(withNearestFaults = True)

def updateNearestEarthquakes(config):
	databaseUrl = '{0}://{1}/{2}'.format(config.database["provider"], config.database["server"], config.database["name"])
	engine = create_engine(databaseUrl, echo=False)
	Session = sessionmaker(bind=engine)
	session = Session()
	query = session.query(earthquakes.Fault)

	for fault in query:
		fault.setNearestEarthquakes(session, 5000)

	session.close()

def main():
	config = configuration.Configuration()
	createDatabase(config)
	updateFaultData(config)
	updateEarthquakeData(config)
	# updateNearestEarthquakes(config)

	print("load complete.")

if __name__ == "__main__":
	main()

from sqlalchemy import create_engine
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

	earthquakes.FocalMechanism.__table__.create(engine)
	earthquakes.MomentTensor.__table__.create(engine)

	print("Loading fault data since this is only done once.")
	qloader = quaternary.QuaternaryLoader(config)
	qloader.update()

	print("Resetting last success date")
	cloader = comcat.ComcatLoader(config)
	cloader.reset()


def updateEarthquakeData(config):
	loader = comcat.ComcatLoader(config)
	loader.update()


def main():
	config = configuration.Configuration()
	createDatabase(config)
	updateEarthquakeData(config)

	print("load complete.")

if __name__ == "__main__":
	main()

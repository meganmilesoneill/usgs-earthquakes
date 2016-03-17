import datetime
import requests
import osgeo.ogr
import os
from zipfile import ZipFile

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import configuration
from models import earthquakes

PATH_TO_FAULTS_SHAPE_FILE = "./qfaults/sectionsALL.shp"

class QuaternaryLoader():
	_config = None

	def __init__(self, config):
		QuaternaryLoader._config = config

	def update(self):
		engine = create_engine('{0}://{1}/{2}'.format(QuaternaryLoader._config.database["provider"], QuaternaryLoader._config.database["server"], QuaternaryLoader._config.database["name"]), echo=False)
		Session = sessionmaker(bind=engine)
		session = Session()

		try:
			if not os.path.exists("qfaults.zip"):
				print("Downloading Quaternary Fault Shape files.")
				qfaults = requests.get(QuaternaryLoader._config.quaternary["shapeFileUrl"])
				with open("qfaults.zip", "wb") as faultdata:
					faultdata.write(qfaults.content)

				print("Extracting Quaternary Fault Shape Files.")
				with ZipFile("qfaults.zip", "r") as zippedfaults:
					zippedfaults.extractall("qfaults")

		except Exception as e:
			print("Error downloading the quaternary shape files from %s\n%s" % (QuaternaryLoader._config.quaternary["shapeFileUrl"], e))
			return

		shapefile = osgeo.ogr.Open(QuaternaryLoader._config.quaternary["shapeFilePath"])
		layer = shapefile.GetLayer(0)

		for feature in layer:
			geometry = feature.GetGeometryRef()

			if geometry is not None:
				name = feature.GetField("name")

				fault = earthquakes.Fault()
				fault.faultid = feature.GetField("fault_id")
				fault.sectionid = feature.GetField("section_id")
				fault.name = name
				fault.fcode = feature.GetField("fcode")
				fault.slipdirect = feature.GetField("slipdirect")
				fault.slipsense = feature.GetField("slipsense")
				fault.slipcode = feature.GetField("slipcode")
				fault.sliprate = feature.GetField("sliprate")
				fault.length = feature.GetField("length")

				fault.agecat = feature.GetField("age")
				try:
					fault.age = int(''.join([c for c in fault.agecat if c not in (',', '<')]))
				except:
					fault.age = 0

				fault.objectid = feature.GetField("objectid")
				fault.facode = feature.GetField("FACODE")
				fault.mappedscal = feature.GetField("mappedscal")
				fault.ftype = feature.GetField("ftype")
				fault.dipdirecti = feature.GetField("dipdirecti")
				fault.num = feature.GetField("num")
				fault.secondaries = feature.GetField("secondarys")
				fault.cooperator = feature.GetField("cooperator")
				fault.acode = feature.GetField("acode")
				fault.azimuth = feature.GetField("azimuth")
				fault.url = feature.GetField("CFM_URL")
				fault.code = feature.GetField("code")
				fault.geometry = geometry.ExportToWkt()

				try:
					session.add(fault)
					session.commit()
					print('creating fault: %s' % name)
				except:
					print('ERROR creating fault: %s\n%s' % (name, sys.exc_info()[0]))
					continue
			else:
				print("no geometry for %s" % name)

		session.close()

	def purge(self):
		pass

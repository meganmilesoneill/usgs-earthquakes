from datetime import datetime, timedelta
#import requests
import grequests

import osgeo.ogr

import json
import sys
import requests

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import configuration
from models import earthquakes

# from sqlalchemy import create_engine

# The USGS FDSN Web Service has limits on the number of earthquake events that
# can be retrieved per request.  In order to pull down all events, requests to
# the web service are broken down into 30-day segments.  Whenever a batch is
# is successfully downloaded from USGS, the timestamp of the most recent earthquake
# is recorded in the loader.config file.  This allows the ComcatLoader to pick up where
# it left off and continue downloading in the case of an interruption of the update
# process or simply to get the latest earthquake events since the late update.

class ComcatLoader():
	_config = None

	def __init__(self, config):
		ComcatLoader._config = config


	def getLastSuccess(self):
		try:
			with open(ComcatLoader._config.comcat["loaderConfigFile"], 'r') as f:
				lastUpdate = f.readline()
				tss = lastUpdate.split("=")[-1]

			ts = float(tss)
			dt = datetime.fromtimestamp(ts)
		except:
			dt = datetime.strptime(ComcatLoader._config.comcat["startDate"], "%m-%d-%Y")

		return dt


	def setLastSuccess(self, dt):
		lastTimestamp = None

		if dt:
			lastTimestamp = str(dt.timestamp())

		with open(ComcatLoader._config.comcat["loaderConfigFile"], 'w') as f:
			f.write("LAST_UPDATE=%s" % lastTimestamp)


	def getNextTimeRange(self):
		startdate = self.getLastSuccess()

		enddate = startdate + timedelta(days=30)

		if(enddate > datetime.utcnow()):
			enddate = None

		return (startdate, enddate)


	def getJsonValue(self, container, keyName, defaultValue = None):
		value = defaultValue
		try:
			value = container[keyName]
		except:
			print("Error retrieving %s" % keyName)

		return value


	def updateEarthquakeFocalMechanism(self, session, earthquake, product):
		#print("updateEarthquakeFocalMechanism starting")
		focalMechanism = earthquakes.FocalMechanism()

		focalMechanism.code = self.getJsonValue(product, "code")
		focalMechanism.preferredWeight = self.getJsonValue(product, "preferredWeight")
		focalMechanism.indexid = self.getJsonValue(product, "indexid")
		focalMechanism.indexTime = self.getJsonValue(product, "indexTime")
		focalMechanism.updateTime = self.getJsonValue(product, "updateTime")
		focalMechanism.source = self.getJsonValue(product, "source")
		focalMechanism.beachballSource = self.getJsonValue(product["properties"], "beachball-source")
		focalMechanism.nodalPlane1Strike = self.getJsonValue(product["properties"], "nodal-plane-1-strike")
		focalMechanism.nodalPlane1Dip = self.getJsonValue(product["properties"], "nodal-plane-1-dip")
		focalMechanism.nodalPlane1Rake = self.getJsonValue(product["properties"], "nodal-plane-1-rake")
		focalMechanism.nodalPlane2Strike = self.getJsonValue(product["properties"], "nodal-plane-2-strike")
		focalMechanism.nodalPlane2Dip = self.getJsonValue(product["properties"], "nodal-plane-2-dip")
		focalMechanism.nodalPlane2Rake = self.getJsonValue(product["properties"], "nodal-plane-2-rake")
		focalMechanism.eventsource = self.getJsonValue(product["properties"], "eventsource")
		focalMechanism.eventsourcecode = self.getJsonValue(product["properties"], "eventsourcecode")
		focalMechanism.eventtime = self.getJsonValue(product["properties"], "eventtime")
		focalMechanism.latitude = self.getJsonValue(product["properties"], "latitude")
		focalMechanism.longitude = self.getJsonValue(product["properties"], "longitude")
		focalMechanism.depth = self.getJsonValue(product["properties"], "depth")
		focalMechanism.reviewStatus = self.getJsonValue(product["properties"], "review-status")
		focalMechanism.evaluationStatus = self.getJsonValue(product["properties"], "evaluation-status")
		focalMechanism.numStationsUsed = self.getJsonValue(product["properties"], "num-stations-used")
		focalMechanism.eventParametersPublicID = self.getJsonValue(product["properties"], "eventParametersPublicID")
		focalMechanism.quakemlPublicid = self.getJsonValue(product["properties"], "quakeml-publicid")

		focalMechanism.earthquake = earthquake
		#print("about to save focalMechanism for %s" % focalMechanism.earthquake.eventid)
		session.add(focalMechanism)
		session.commit()
		#print("updateEarthquakeFocalMechanism complete")


	def updateEarthquakeDetail(self, session, earthquake):
		try:
			loadDetail = False
			productsToLoad = ComcatLoader._config.comcat["productsToLoad"].split(",")
			for productName in productsToLoad:
				if productName in earthquake.types:
					loadDetail = True
					break;

			if not loadDetail:
				return

			print("loading detailUrl: %s" % earthquake.detail)
			response = requests.get(earthquake.detail)
			if response is None:
				print("Detail url not loaded")
				return

			detailJson = response.json()
			print("getting products")
			products = self.getJsonValue(detailJson["properties"], "products")

			print("iterating through products")
			for productName in products:
				if productName in productsToLoad:
					print("getting product list for productType: %s" % productName)
					productList = products[productName]

					for product in productList:
						if product["type"] == "focal-mechanism":
							self.updateEarthquakeFocalMechanism(session, earthquake, product)

		except Exception as e:
			print("ERROR importing earthquake details:", e)

	def processDetailError(self, request, exception):
		print("Request failed: %s" % exception)

	def processDetailResponse(self, response, **kwargs):
		engine = create_engine('{0}://{1}/{2}'.format(ComcatLoader._config.database["provider"], ComcatLoader._config.database["server"], ComcatLoader._config.database["name"]), echo=False)
		Session = sessionmaker(bind=engine)
		session = Session()

		try:
			print("processing detail response - starting")
			detailJson = response.json()

			earthquakeid = "{0}{1}".format(self.getJsonValue(detailJson["properties"], "net"), self.getJsonValue(detailJson["properties"], "code"))
			products = self.getJsonValue(detailJson["properties"], "products")
			print("processing detail for eventid: %s" % earthquakeid)

			productsToLoad = ComcatLoader._config.comcat["productsToLoad"].split(",")

			earthquake = session.query(earthquakes.Earthquake).filter_by(eventid = earthquakeid).first()

			for productName in products:
				if productName in productsToLoad:
					print("getting product list for productType: %s" % productName)
					productList = products[productName]

					for product in productList:
						if product["type"] == "focal-mechanism":
							self.updateEarthquakeFocalMechanism(session, earthquake, product)


			print("processing detail response - complete")
		except Exception as e:
			print("ERROR processing detail response: %s" % e)
		finally:
			session.close()

	def updateEarthquakes(self, session, startdate, enddate = None):

		detailUrlRequests = []
		productsToLoad = ComcatLoader._config.comcat["productsToLoad"].split(",")

		queryString = "starttime=%s" % startdate.strftime("%Y-%m-%d")
		if (enddate is not None):
			queryString += "&endtime=%s" % enddate.strftime("%Y-%m-%d")
		queryString += "&orderby=time-asc&eventtype=earthquake"

		url = ComcatLoader._config.comcat["apiUrl"] % queryString
		print("Importing earthquake data from: %s" % url)

		datasource = osgeo.ogr.Open(url)
		if not datasource:
			sys.exit("ERROR: Cannot open comcat url: %s" % url)

		layer = datasource.GetLayer('OGRGeoJSON')


		i = 0
		total = layer.GetFeatureCount()
		ts = self.getLastSuccess()

		for feature in layer:
			i += 1
			progress_text = "....... (%s of %s) %3.2f%% complete" % (i, total, i/total * 100)
			loadDetail = False

			geometry = feature.GetGeometryRef()

			if geometry is not None:
				wkt = geometry.ExportToWkt()
				detailUrl = feature.GetField("detail")
				eventid = feature.GetField("id")

				types = feature.GetField("types")
				for productName in productsToLoad:
					if productName in types:
						loadDetail = True
						break;


				ts = feature.GetField("time") / 1000

				earthquake = earthquakes.Earthquake()
				earthquake.eventid = feature.GetField("id")
				earthquake.mag = feature.GetField("mag")
				earthquake.place = feature.GetField("place")
				earthquake.time = feature.GetField("time")
				earthquake.updated = feature.GetField("updated")
				earthquake.tz = feature.GetField("tz")
				earthquake.url = feature.GetField("url")
				earthquake.detail = detailUrl
				earthquake.felt = feature.GetField("felt")
				earthquake.cdi = feature.GetField("cdi")
				earthquake.mmi = feature.GetField("mmi")
				earthquake.alert = feature.GetField("alert")
				earthquake.status = feature.GetField("status")
				earthquake.tsunami = feature.GetField("tsunami")
				earthquake.sig = feature.GetField("sig")
				earthquake.net = feature.GetField("mag")
				earthquake.code = feature.GetField("code")
				earthquake.ids = feature.GetField("ids")
				earthquake.sources = feature.GetField("sources")
				earthquake.types = types
				earthquake.nst = feature.GetField("nst")
				earthquake.dmin = feature.GetField("dmin")
				earthquake.rms = feature.GetField("rms")
				earthquake.gap = feature.GetField("gap")
				earthquake.magType = feature.GetField("magType")
				earthquake.eventType = feature.GetField("type")
				earthquake.title = feature.GetField("title")
				earthquake.geometry = wkt

				try:
					session.add(earthquake)
					print('earthquake record created: %s' % progress_text)
					session.commit()
					if loadDetail:
						print("adding url to queue: %s" % detailUrl)
						detailUrlRequests.append(grequests.get(detailUrl, hooks = {'response': self.processDetailResponse }))
						if(len(detailUrlRequests) >= 10):
							print("loading detail (%d) urls" % len(detailUrlRequests))
							grequests.map(detailUrlRequests, exception_handler=self.processDetailError)
							detailUrlRequests = []

				except Exception as e:
					print('ERROR creating earthquake record: %s\n%s' % (progress_text, e))
					continue
			else:
				print("no geometry for %s" % feature.GetField("eventid"))

		if(len(detailUrlRequests) > 0):
			print("loading detail (%d) urls" % len(detailUrlRequests))
			grequests.map(detailUrlRequests, exception_handler=self.processDetailError)
			detailUrlRequests = []
		self.setLastSuccess(datetime.utcfromtimestamp(ts))


	def update(self):
		engine = create_engine('{0}://{1}/{2}'.format(ComcatLoader._config.database["provider"], ComcatLoader._config.database["server"], ComcatLoader._config.database["name"]), echo=False)
		Session = sessionmaker(bind=engine)
		session = Session()
		startdate, enddate = self.getNextTimeRange()

		print("Next time range: %s - %s" % (str(startdate), str(enddate)))

		today = datetime.utcnow()

		while(startdate <= today):
			print("Importing next range")
			self.updateEarthquakes(session, startdate, enddate)

			startdate, enddate = self.getNextTimeRange()

		session.close()
		print("Update complete.")


	def purge(self):
		self.setLastSuccess(None)
		# TODO: Add call to delete all earthquakes and products


	def reset(self):
		self.setLastSuccess(None)

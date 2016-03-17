import unittest
import os

from .context import configuration
from .context import comcat
from datetime import datetime, timedelta

class TestComcatLoader(unittest.TestCase):

	def test_getLastSuccessFromInitialState(self):
		config = configuration.Configuration("test")
		# delete config file
		try:
			os.remove(config.comcat["loaderConfigFile"])
		except:
			pass

		loader = comcat.ComcatLoader(config)
		self.assertEqual(datetime.strptime(config.comcat["startDate"], "%m-%d-%Y"), loader.getLastSuccess())

	def test_setLastSuccess(self):
		config = configuration.Configuration("test")
		loader = comcat.ComcatLoader(config)

		dt = datetime.utcnow()

		loader.setLastSuccess(dt)
		self.assertEqual(dt, loader.getLastSuccess())

	def test_getNextRangeFromInitialState(self):
		config = configuration.Configuration("test")
		try:
			os.remove(config.comcat["loaderConfigFile"])
		except:
			pass

		loader = comcat.ComcatLoader(config)
		earliestDate = datetime.strptime(config.comcat["startDate"], "%m-%d-%Y")

		startdate, enddate = loader.getNextTimeRange()

		self.assertEqual(earliestDate, startdate)
		self.assertEqual(earliestDate + timedelta(days=30), enddate)

	def test_getNextRange(self):
		config = configuration.Configuration("test")

		loader = comcat.ComcatLoader(config)
		lastSuccessDate = loader.getLastSuccess()
		expectedEndDate = lastSuccessDate + timedelta(days=30)

		if expectedEndDate > datetime.utcnow():
			expectedEndDate = None

		startdate, enddate = loader.getNextTimeRange()

		self.assertEqual(lastSuccessDate, startdate)
		self.assertEqual(expectedEndDate, enddate)


if __name__ == "__main__":
	unittest.main()

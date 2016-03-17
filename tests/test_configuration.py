import unittest
from .context import configuration

class TestConfiguration(unittest.TestCase):

	def test_loadTestConfig(self):
		testConfig = configuration.Configuration("test")
		self.assertEqual(testConfig.database["name"], "usgs-earthquakes-test")

if __name__ == "__main__":
	unittest.main()

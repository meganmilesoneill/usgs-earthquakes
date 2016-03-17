import json
import sys

class Configuration():

    def __init__(self, env = "default"):
        try:
            #print("Loading configuration with env=%s" % env)
            with open('./configuration.json') as json_data_file:
                data = json.load(json_data_file)

            config_dict = json.dumps(data[env])
            self.__dict__ = json.loads(config_dict)

            # TODO: Implement logic to load "default" config and override
            # values with specified config if provided
        except Exception as e:
            print ("Error loading configuration file: {0}".format(e))
            sys.exit()

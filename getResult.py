import codecs
import os
import tempfile
import time

from model.Configuration import Configuration
from algorithm.GeneticAlgorithm import GeneticAlgorithm
from Output import get_result
from HtmlOutput import HtmlOutput

start_time = int(round(time.time() * 1000))
configuration = Configuration()

# Replace 'your_config_file.json' with the actual path to your JSON file
file_name = 'input3.json'
configuration.parse_file(file_name)

alg = GeneticAlgorithm(configuration)
alg.run(9999, 0.95)

get_result(alg.result)
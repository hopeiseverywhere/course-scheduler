import time

from model.Configuration import Configuration
from algorithm.GeneticAlgorithm import GeneticAlgorithm
from Output import get_result

def get_result(json):

    start_time = int(round(time.time() * 1000))
    configuration = Configuration()

    file_name = json
    configuration.parse_file(file_name)

    alg = GeneticAlgorithm(configuration)
    alg.run(9999, 0.99)

    get_result(alg.result)

    seconds = (int(round(time.time() * 1000)) - start_time) / 1000.0
    print("\nCompleted in {} secs.\n".format(seconds))

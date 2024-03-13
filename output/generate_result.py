import time

from model.Configuration import Configuration
from algorithm.GeneticAlgorithm import GeneticAlgorithm
from api.Output import get_result

def generate_result(json_data, min_accuracy=0.90):
    """generate genetic algorithm result for the api

    Args:
        json_data (_type_): input data
        min_accuracy (float, optional): minimum accuracy for the GA. Defaults to 0.90.

    Returns:
        string: json string
    """
    start_time = int(round(time.time() * 1000))
    configuration = Configuration()

    try:

        configuration.parse_file(json_data)
        print("Parsing file completed.")

        alg = GeneticAlgorithm(configuration)
        print("Genetic algorithm initialized.")

        alg.run(9999, min_accuracy)
        print("Genetic algorithm run completed.")

        json_string = get_result(alg.result)
        print("Result obtained successfully.")


        seconds = (int(round(time.time() * 1000)) - start_time) / 1000.0
        print("\nCompleted in {} secs.\n".format(seconds))
        return json_string
    except Exception as e:
        print("Error:", e)

def run(alg: GeneticAlgorithm, min_accuracy=0.90):
    alg.run(9999, min_accuracy)
    return get_result(alg.result)

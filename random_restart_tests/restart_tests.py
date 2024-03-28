import codecs
import os
import tempfile
import time


from model.Configuration import Configuration
from algorithm.GeneticAlgorithm import GeneticAlgorithm
from io_data.input.testData import data
import csv


def local_app():
    # Testing regular method
    configuration = Configuration()
    configuration.parse_file(data)
    for i in range(20):
        start_time = int(round(time.time() * 1000))
        best = GeneticAlgorithm(configuration)
        best.run(9999, 0.999)
        seconds = (int(round(time.time() * 1000)) - start_time) / 1000.0
        with open('output.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([0, i, best.current_generation, seconds])
        print("Finished standard, iteration {}".format(i))

    # Testing restart method
    for i in range(20):
        start_time = int(round(time.time() * 1000))
        max_generations = 1250 // 2
        min_fitness = 0.999
        running = True
        best = None
        attempts = 0  # for testing
        final_iterations = 0
        while running:
            attempts += 1
            alg = GeneticAlgorithm(configuration)
            alg.run(max_generations, min_fitness)
            final_iterations = alg.current_generation
            if best is None or alg.result.fitness > best.result.fitness:
                best = alg
            if best.result.fitness >= min_fitness:
                # print("Took {} attempts to find a solution".format(attempts))
                break
        seconds = (int(round(time.time() * 1000)) - start_time) / 1000.0
        with open('output.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([1, i, 1250 * (attempts - 1) + final_iterations, seconds])
        print("Finished new, iteration {}".format(i))

if __name__ == '__main__':
    local_app()
import codecs
import os
import tempfile
import time


from model.Configuration import Configuration
from algorithm.GeneticAlgorithm import GeneticAlgorithm
from io_data.input.testData import data
import csv
import multiprocessing as mp


def restart_tests():
    max_repeat = 5000
    min_fitness = 0.99
    iterations = 200
    # Testing regular method
    for i in range(iterations):
        start_time = int(round(time.time() * 1000))
        configuration = Configuration()
        configuration.parse_file(data)
        solution = GeneticAlgorithm(configuration)
        manager = mp.Manager()
        result = manager.dict()
        keep_searching = manager.Event()
        solution.run(keep_searching, result, max_repeat, min_fitness)
        seconds = (int(round(time.time() * 1000)) - start_time) / 1000.0
        with open('output.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([0, i, solution.current_generation, seconds])
        print("Finished standard, iteration {}".format(i))

    # Testing parallel method
    for j in range(iterations):
        start_time = int(round(time.time() * 1000))

        # Arguments of multiprocessor pool
        pool_size = min(5, os.cpu_count() - 1)
        process_list = []
        manager = mp.Manager()
        result = manager.dict()
        keep_searching = manager.Event()
        keep_searching.set()

        # Create the processes and start them
        for i in range(pool_size):
            configuration = Configuration()
            configuration.parse_file(data)
            alg = GeneticAlgorithm(configuration)
            process_list.append(mp.Process(target=alg.run, args=(keep_searching, result, max_repeat, min_fitness)))
            process_list[i].start()

        # Block until a configuration is found
        for process in process_list:
            process.join()

        # Get best result (first solution that satisfies constraints to be found)
        solution = result['solution']
        seconds = (int(round(time.time() * 1000)) - start_time) / 1000.0

        # Ensure a solution was actually found
        if solution is not None:
            current_generation = solution.current_generation
        else:
            current_generation = max_repeat * 2

        # Write results to csv
        with open('output.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([2, j, current_generation, seconds])
        print("Finished parallel, iteration {}".format(j))

    # # Testing restart method
    # for i in range(20):
    #     configuration = Configuration()
    #     configuration.parse_file(data)
    #     start_time = int(round(time.time() * 1000))
    #     max_generations = 1250 // 2
    #     min_fitness = 0.999
    #     running = True
    #     best = None
    #     attempts = 0  # for testing
    #     final_iterations = 0
    #     while running:
    #         attempts += 1
    #         alg = GeneticAlgorithm(configuration)
    #         alg.run(max_generations, min_fitness)
    #         final_iterations = alg.current_generation
    #         if best is None or alg.result.fitness > best.result.fitness:
    #             best = alg
    #         if best.result.fitness >= min_fitness:
    #             # print("Took {} attempts to find a solution".format(attempts))
    #             break
    #     seconds = (int(round(time.time() * 1000)) - start_time) / 1000.0
    #     with open('output.csv', 'a', newline='') as csvfile:
    #         writer = csv.writer(csvfile)
    #         writer.writerow([1, i, 1250 * (attempts - 1) + final_iterations, seconds])
    #     print("Finished new, iteration {}".format(i))

if __name__ == '__main__':
    restart_tests()

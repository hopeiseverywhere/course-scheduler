from model.Schedule import Schedule
import random
from random import randrange
from time import time


# Lakshmi, R. et al. “A New Biological Operator in Genetic Algorithm for Class Scheduling Problem.”
# International Journal of Computer Applications 60 (2012): 6-11.
# Copyright (c) 2020 - 2022 Miller Cy Chan


# Genetic algorithm
class GeneticAlgorithm:
    def init_algorithm(self, prototype, number_of_chromosomes=100,
        replace_by_generation=8, track_best=5):
        # Number of best chromosomes currently saved in best chromosome group
        self._current_best_size = 0
        # Prototype of chromosomes in population
        self._prototype = prototype

        # there should be at least 2 chromosomes in population
        if number_of_chromosomes < 2:
            number_of_chromosomes = 2

        # and algorithm should track at least on of best chromosomes
        if track_best < 1:
            track_best = 1

        # Population of chromosomes
        self._chromosomes = number_of_chromosomes * [None]
        # Inidicates whether chromosome belongs to best chromosome group
        self._best_flags = number_of_chromosomes * [False]

        # Indices of best chromosomes
        self._best_chromosomes = track_best * [0]
        # Number of chromosomes which are replaced in each generation by offspring
        self.set_replace_by_generation(replace_by_generation)

    # Initializes genetic algorithm
    def __init__(self, configuration, number_of_crossover_points=2, mutation_size=2, crossoverProbability=80,
                 mutation_probability=3):
        self.init_algorithm(Schedule(configuration))
        self._mutationSize = mutation_size
        self._numberOfCrossoverPoints = number_of_crossover_points
        self._crossover_probability = crossoverProbability
        self._mutationProbability = mutation_probability

    @property
    # Returns pointer to best chromosomes in population
    def result(self):
        return self._chromosomes[self._best_chromosomes[0]]

    def set_replace_by_generation(self, value):
        number_of_chromosomes = len(self._chromosomes)
        trackBest = len(self._best_chromosomes)
        if (value > number_of_chromosomes - trackBest):
            value = number_of_chromosomes - trackBest
        self._replace_by_generation = value

    # Tries to add chromosomes in best chromosome group
    def add_to_best(self, chromosomeIndex):
        best_chromosomes = self._best_chromosomes
        length_best = len(best_chromosomes)
        best_flags = self._best_flags
        chromosomes = self._chromosomes

        # don't add if new chromosome hasn't fitness big enough for best chromosome group
        # or it is already in the group?
        if (self._current_best_size == length_best and chromosomes[best_chromosomes[self._current_best_size - 1]].fitness >=
            chromosomes[chromosomeIndex].fitness) or best_flags[chromosomeIndex]:
            return

        # find place for new chromosome
        j = self._current_best_size
        for i in range(j, -1, -1):
            j = i
            pos = best_chromosomes[i - 1]
            # group is not full?
            if i < length_best:
                # position of new chromosomes is found?
                if chromosomes[pos].fitness > chromosomes[chromosomeIndex].fitness:
                    break

                # move chromosomes to make room for new
                best_chromosomes[i] = pos
            else:
                # group is full remove worst chromosomes in the group
                best_flags[pos] = False

        # store chromosome in best chromosome group
        best_chromosomes[j] = chromosomeIndex
        best_flags[chromosomeIndex] = True

        # increase current size if it has not reached the limit yet
        if self._current_best_size < length_best:
            self._current_best_size += 1

    # Returns TRUE if chromosome belongs to best chromosome group
    def is_in_best(self, chromosome_index) -> bool:
        return self._best_flags[chromosome_index]

    # Clears best chromosome group
    def clear_best(self):
        self._best_flags = len(self._best_flags) * [False]
        self._current_best_size = 0

    # initialize new population with chromosomes randomly built using prototype
    def initialize(self, population):
        # addToBest = self.addToBest
        prototype = self._prototype
        length_chromosomes = len(population)

        for i in range(0, length_chromosomes):
            # add new chromosome to population
            population[i] = prototype.make_new_from_prototype()
            # addToBest(i)

    def selection(self, population):
        length_chromosomes = len(population)
        return (population[randrange(32768) % length_chromosomes],
                population[randrange(32768) % length_chromosomes])

    def replacement(self, population, replace_by_generation) -> []:
        mutation_size = self._mutationSize
        number_of_crossover_points = self._numberOfCrossoverPoints
        crossover_probability = self._crossover_probability
        mutation_probability = self._mutationProbability
        selection = self.selection
        is_in_best = self.is_in_best
        length_chromosomes = len(population)
        # produce offspring
        offspring = replace_by_generation * [None]
        for j in range(replace_by_generation):
            # selects parent randomly
            parent = selection(population)

            offspring[j] = parent[0].crossover(
                parent[1], number_of_crossover_points, crossover_probability)
            offspring[j].mutation(mutation_size, mutation_probability)

            # replace chromosomes of current operation with offspring
            # select chromosome for replacement randomly
            ci = randrange(32768) % length_chromosomes
            while is_in_best(ci):
                ci = randrange(32768) % length_chromosomes

            # replace chromosomes
            population[ci] = offspring[j]

            # try to add new chromosomes in best chromosome group
            self.add_to_best(ci)
        return offspring

    # Starts and executes algorithm
    def run(self, max_repeat=9999, min_fitness=0.999):
        # clear best chromosome group from previous execution
        self.clear_best()
        length_chromosomes = len(self._chromosomes)

        self.initialize(self._chromosomes)
        random.seed(round(time() * 1000))

        # Current generation
        current_generation = 0

        repeat = 0
        last_best_fit = 0.0

        while 1:
            best = self.result
            print("Fitness:", "{:f}\t".format(best.fitness),
                  "Generation:", current_generation, end="\r")

            # algorithm has reached criteria?
            if best.fitness > min_fitness:
                break

            difference = abs(best.fitness - last_best_fit)
            if difference <= 0.0000001:
                repeat += 1
            else:
                repeat = 0

            if repeat > (max_repeat / 100):
                random.seed(round(time() * 1000))
                self.set_replace_by_generation(self._replace_by_generation * 3)
                self._crossover_probability += 1

            self.replacement(self._chromosomes, self._replace_by_generation)

            last_best_fit = best.fitness
            current_generation += 1

    def __str__(self):
        return "Genetic Algorithm"

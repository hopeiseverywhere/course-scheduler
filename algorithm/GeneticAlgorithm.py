from model.Schedule import Schedule
from model.Configuration import Configuration
import random
from random import randrange
from time import time


class GeneticAlgorithm:

    def init_algorithm(self, prototype: Schedule,
        number_of_chromosomes=100, replace_by_generation=8, track_best=5):
        # Number of the best chromosomes currently
        # saved in the best chromosome group
        self._current_best_size = 0
        # Prototype of chromosomes in population
        self._prototype = prototype
        # there should be at least 2 chromosomes in population
        if number_of_chromosomes < 2:
            number_of_chromosomes = 2
        # and algorithm should track at least one of best chromosomes
        if track_best < 1:
            track_best = 1

        # Population of chromosomes
        self._chromosomes = number_of_chromosomes * [None]
        # Indicates whether chromosome belongs to the best chromosome group
        self._best_flags = number_of_chromosomes * [False]

        # Indices of best chromosomes
        self._best_chromosomes = track_best * [0]
        # Number of chromosomes which are replaced in each generation
        # by offspring
        self.set_replace_by_generation(replace_by_generation)

    def __init__(self,
        configuration,
        crossover_pts=2,
        mutation_size=2,
        crossover_prob=95,
        mutation_prob=1):
        """

        :type configuration: Configuration
        """

        prototype = Schedule(configuration)
        self.init_algorithm(prototype)
        self._mutation_size = mutation_size
        self._crossover_points = crossover_pts
        self._crossover_prob = crossover_prob
        self._mutation_prob = mutation_prob

    def run(self, max_repeat=9999, min_fitness=0.99, timeout=None):
        # clear best chromosome group from previous execution
        self.clear_best()
        self.initialize(self._chromosomes)
        random.seed(round(time() * 1000))
        # current generation
        current_generation = 0
        repeat = 0
        last_best_fit = 0.0
        start_time = time()

        while True:
            elapsed_time = time() - start_time
            if timeout and elapsed_time >= timeout:
                raise TimeoutError("Algorithm execution exceeded the specified timeout")
            
            best = self.result
            print("Fitness:", "{:f}\t".format(best.fitness),
                  "Generation:", current_generation, end="\r")
            # reached best
            if best.fitness > min_fitness:
                break
            if current_generation >= max_repeat * 2:
                print()
                print(self.result._fitness)
                break
            
            difference = abs(best.fitness - last_best_fit)
            if difference <= 0.0000001:
                repeat += 1
            else:
                repeat = 0

            if repeat >= (max_repeat / 100):
                random.seed(round(time() * 1000))
                self.set_replace_by_generation(self._replace_by_generation * 3)
                self._crossover_prob += 1

            self.replacement(self._chromosomes, self._replace_by_generation)

            last_best_fit = best.fitness
            current_generation += 1
            

    def is_in_best(self, chromosome_index) -> bool:
        """
        Returns TRUE if chromosome belongs to the best chromosome group
        :param chromosome_index:
        :return:
        """
        return self._best_flags[chromosome_index]

    def selection(self, population):
        length_chromosomes = len(population)
        return (population[randrange(32768) % length_chromosomes],
                population[randrange(32768) % length_chromosomes])

    def add_to_best(self, chromosome_index):
        """
        add chromosomes in to the best chromosome group
        :param chromosome_index:
        :return:
        """
        best_chromosomes = self._best_chromosomes
        length_best = len(best_chromosomes)
        best_flags = self._best_flags
        chromosomes = self._chromosomes
        # don't add if new chromosome hasn't fitness big enough f
        # or best chromosome group
        # or it is already in the group?
        if ((self._current_best_size == length_best
             and chromosomes[
                 best_chromosomes[self._current_best_size - 1]].fitness
             >= chromosomes[chromosome_index].fitness) or
            best_flags[chromosome_index]):
            return

        # find place for new chromosome
        j = self._current_best_size
        for i in range(j, -1, -1):
            j = i
            pos = best_chromosomes[i - 1]
            # group is not full?
            if i < length_best:
                # position of new chromosomes is found?
                if chromosomes[pos].fitness > chromosomes[
                    chromosome_index].fitness:
                    break
                # move chromosomes to make room for new
                best_chromosomes[i] = pos
            else:
                # group is full, remove worst in the group
                best_flags[pos] = False

        # store chromosomes in the best chromosome group
        best_chromosomes[j] = chromosome_index
        best_flags[chromosome_index] = True

        # increase current size if it has not reached the limit yes
        if self._current_best_size < length_best:
            self._current_best_size += 1

    def replacement(self, population, replace_by_generation):
        mutation_size = self._mutation_size
        crossover_points = self._crossover_points
        crossover_prob = self._crossover_prob
        mutation_prob = self._mutation_prob
        selection = self.selection
        is_in_best = self.is_in_best
        length_chromosomes = len(population)

        # produce offspring
        offspring = replace_by_generation * [None]
        for j in range(replace_by_generation):
            # selects parent randomly
            parent = selection(population)
            offspring[j] = parent[0].crossover(
                parent[1], crossover_points,
                crossover_prob
            )
            offspring[j].mutation(mutation_size, mutation_prob)

            # replace chromosomes of current operation with offspring
            # select chromosome for replacement randomly
            ci = randrange(32768) % length_chromosomes
            while is_in_best(ci):
                ci = randrange(32768) % length_chromosomes

            # replace chromosomes
            population[ci] = offspring[j]

            # try to add new chromosomes in the best chromosome group

    def set_replace_by_generation(self, value):
        number_of_chromosomes = len(self._chromosomes)
        track_best = len(self._best_chromosomes)
        if (value > number_of_chromosomes - track_best):
            value = number_of_chromosomes - track_best
        self._replace_by_generation = value

    def clear_best(self):
        """
        clear the best chromosome group
        :return:
        """
        self._best_flags = len(self._best_flags) * [False]
        self._current_best_size = 0

    def initialize(self, population):
        """
        initialize new population with chromosomes
        randomly built using prototype
        :param population:
        :return:
        """
        # add_to_best = self.add_to_best
        prototype = self._prototype
        length_chromosomes = len(population)

        # print("length population", length_chromosomes)
        for i in range(0, length_chromosomes):
            # add new chromosome to population

            population[i] = prototype.make_new_from_prototype()
            # add_to_best(i)

    def cleanup(self):
        """
        Perform cleanup tasks and deallocate resources.
        """
        self.clear_best()  # Clear best chromosome group
        self._chromosomes = None  # Set reference to chromosomes list to None
        self._best_flags = None  # Set reference to best flags list to None
        self._best_chromosomes = None  # Set reference to best chromosomes list to None
        self._prototype = None  # Set reference to prototype to None

    @property
    def result(self):
        return self._chromosomes[self._best_chromosomes[0]]

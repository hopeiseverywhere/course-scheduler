import random
from random import randrange

from model import Constant
import numpy as np
from random import randrange

from model.Cirteria import Criteria
from model.Reservation import Reservation
from model.Section import Section
from model.Configuration import Configuration


class Schedule:
    """
    Schedule chromosome
    """
    DAY_NUM, DAY_HOURS = Constant.DAYS_NUM, Constant.DAY_SLOTS

    def __init__(self, configuration: Configuration):
        self._configuration = configuration
        # Fitness value of chromosome
        self._fitness = 0

        # Time-space slots, one entry represent one hour in one classroom
        slots_length = (Constant.DAYS_NUM * Constant.DAY_SLOTS
                        * self._configuration.number_of_rooms)
        self._slots = [[] for _ in range(slots_length)]

        # Section table for chromosome
        # Used to determine first time-space slot used by sections
        self._sections_table = {}

        # Flags of section requirements satisfaction
        self._criteria = np.zeros(
            self._configuration.number_of_sections * len(Criteria.weights),
            dtype=bool)

        # Initialize diversity value to 0
        self._diversity = 0.0
        # Initialize rank value to 0
        self._rank = 0
        # Initialize converted objectives list
        self._converted_objectives = []
        # Initialize objectives list
        self._objectives = []

    def __str__(self):

        pass

    def copy(self, other: 'Schedule', setup_only: bool):
        if setup_only:
            # print("Set up only = true")
            return Schedule(other.configuration)
        if not setup_only:
            # print("Set up only = false")
            self._configuration = other.configuration
            # copy code
            self._slots = [row[:] for row in other.slots]
            self._sections_table = {key: value for key, value in
                                    other.sections_table.items()}

            # copy flags of section requirement
            self._criteria = other.criteria[:]
            self._objectives = other.objectives[:]

            # copy fitness
            self._fitness = other.fitness
            if other.converted_objectives is not None:
                self._converted_objectives = other.converted_objectives[:]
            return self


    def random_selection(self, section: Section):
        """
        Make random selection of (day, time, room_id) from a give section
        :param section:
        :return: tuple (day, start_time, room_id)
        """

        dur = section.duration
        pref_range = section.pref_time_range
        number_of_students = section.number_of_students
        number_of_students = Configuration.round_down_to_nearest_five(
            number_of_students)
        day = randrange(Schedule.DAY_NUM)
        room_id = random.choice(
            self._configuration.rooms_by_capacity[number_of_students])
        # room = randrange(number_of_rooms)
        start_time = randrange(pref_range[1] - dur)
        return day, start_time, room_id

    def make_new_from_prototype(self, positions=None):
        """
        make new chromosome with same setup but with randomly chosen code
        :param positions:
        :return:
        """
        # make new chromosome, copy chromosome setup
        new_chromosome = self.copy(self, True)

        new_chromosome_slots = new_chromosome._slots
        new_chromosome_sections_table = new_chromosome._sections_table

        # place sections at random position
        sections = self._configuration.sections
        number_of_rooms = self._configuration.number_of_rooms

        # determine a random position of a section
        for section in sections:
            # dur = section.duration
            # pref_range = section.pref_time_range
            # number_of_students = section.number_of_students
            # number_of_students = Configuration.round_down_to_nearest_five(number_of_students)
            #
            # day = randrange(DAY_NUM)
            # room_id = random.choice(self._configuration.rooms_by_capacity[number_of_students])
            # # room = randrange(number_of_rooms)
            # time = randrange(pref_range[1] - dur)

            day, start_time, room_id = self.random_selection(section)
            section.set_all(day, start_time, room_id)

            reservation = Reservation.get_reservation(number_of_rooms
                                                      , day, start_time, room_id)
            if positions is not None:
                positions.append(day) # day
                positions.append(room_id) # room id
                positions.append(start_time) # stat time
            reservation_index = hash(reservation)
            # fill time space slots for each hour of sections
            for i in range(section.duration - 1, -1, -1):
                new_chromosome_slots[reservation_index + i].append(section)

            # insert in section table of chromosome
            new_chromosome_sections_table[section] = reservation_index

        new_chromosome.get_fitness()
        return new_chromosome

    def crossover(self, parent, number_of_crossover_points,
        crossover_prob):
        """
        Performs crossover operation using to
        chromosomes and returns pointer to offspring
        :param parent:
        :param number_of_crossover_points:
        :param crossover_prob:
        :return:
        """
        # check probability of crossover operation
        if randrange(100) > crossover_prob:
            # no crossover, just copy first parent
            return self.copy(self, False)

        # new chromosome object, copy chromosome setup
        offspring = self.copy(self, True)
        offspring_sections_table, offspring_slots = (
            offspring._sections_table, offspring._slots)

        sections = self._sections_table
        course_sections = tuple(sections.keys())
        parent_sections = parent.sections_table
        parent_course_sections = tuple(parent.sections_table.keys())

        # number of sections
        size = len(sections)

        cp = size * [False]

        # determine crossover point (randomly)
        for i in range(number_of_crossover_points, 0, -1):
            check_point = False
            while not check_point:
                p = randrange(size)
                if not cp[p]:
                    cp[p] = check_point = True

        # make new code by combining parent codes
        first = randrange(2) == 0

        for i in range(size):
            if first:
                course_section = course_sections[i]
                dur = course_section.duration
                reservation_index = sections[course_section]
                # insert class from first parent
                # into new chromosome's class table
                offspring_sections_table[course_section] = reservation_index
                # all time-space slots of class are copied
                for j in range(dur - 1, -1, -1):
                    offspring_slots[reservation_index + j].append(
                        course_section)
            else:
                course_section = parent_course_sections[i]
                dur = course_section.duration
                reservation_index = parent_sections[course_section]
                # insert class from second parent
                # into new chromosome's class table
                offspring_sections_table[course_section] = reservation_index
                # all time-space slots of class are copied
                for j in range(dur - 1, -1, -1):
                    offspring_slots[reservation_index + j].append(
                        course_section)

            # crossover point
            if cp[i]:
                # change source chromosome
                first = not first

        offspring.get_fitness()

        # return smart pointer to offspring
        return offspring

    def repair(self, section: Section, reservation_idx:
    int, reservation: Reservation):
        # extract relevant prams and constant
        number_of_rooms = self._configuration.number_of_rooms
        DAY_HOURS, DAYS_NUM = Constant.DAY_SLOTS, Constant.DAYS_NUM
        slots = self.slots
        dur = section.duration

        # if reservation index is provided, remove section hour from
        # current time-space slot
        if reservation_idx > -1:
            for j in range(dur):
                sections = slots[reservation_idx + j]
                while section in sections:
                    sections.remove(section)

        # determine the position of the section
        if reservation is None:
            day, start_time, room_id = self.random_selection(section)
            section.set_all(day, start_time, room_id)

            reservation = Reservation.get_reservation(number_of_rooms
                                                      , day, start_time, room_id)
        # calculate the index of reservation
        reservation_idx = hash(reservation)

        # move the section hour to the new time-space slot
        for j in range(dur):
            slots[reservation_idx + j].append(section)

        # Update the entry of the section table
        # to point to the new time-space slots
        self._sections_table[section] = reservation_idx

    def mutation(self, mutation_size, mutation_prob):
        # check probability of mutation operation
        if randrange(100) > mutation_prob:
            return

        sections_table = self._sections_table

        # number of sections
        number_of_sections = len(sections_table)
        course_sections = tuple(sections_table.keys())
        configuration = self._configuration
        # number_of_rooms = configuration.number_of_rooms

        # move selected number of sections at random position
        for i in range(mutation_size, 0, -1):
            # select random chromosome for movement
            move_pos = randrange(number_of_sections)

            # current time-space slot used by class
            section = course_sections[move_pos]
            reservation_index = sections_table[section]

            self.repair(section, reservation_index, None)

        self.get_fitness()

    def get_fitness(self):
        """
        calculate fitness value of chromosome
        :return:
        """
        # increment value when criteria violation occurs
        self._objectives = np.zeros(len(Criteria.weights))

        # chromosome's score
        score = 0
        criteria = self._criteria
        configuration = self._configuration
        items = self._sections_table.items()
        slots = self._slots
        number_of_rooms = configuration.number_of_rooms
        # DAY_NUM, DAY_HOURS = Constant.DAYS_NUM, Constant.DAY_SLOTS
        day_size = Schedule.DAY_HOURS * number_of_rooms

        ci = 0
        get_room_by_id = configuration.get_room_by_id
        # check criteria cna calculate scores for each section in schedule

        for section, reservation_index in items:
            reservation = Reservation.parse(reservation_index)

            # coordinates of time-space slot
            day, time, room = (reservation.day,
                               reservation.time, reservation.room_id)

            dur = section.duration

            ro = Criteria.is_room_overlapped(slots, reservation, dur)
            # 1. check room overlapping
            criteria[ci + 0] = not ro

            r = get_room_by_id(room)
            # 2. does curr room have enough seats
            es = Criteria.is_seat_enough(r, section)
            criteria[ci + 1] = es

            # 3. is professor overlap
            time_id = day * day_size + time
            po = Criteria.is_prof_overlapped(slots, section,
                                             number_of_rooms, time_id)
            criteria[ci + 2] = not po
            # 4. if professor preference time satisfied
            start_time = time
            end_time = start_time + dur

            pfo = Criteria.is_prof_satisfied(section, start_time, end_time)
            # print("ro:", ro)
            # print("es:", es)
            # print("po:", po)
            # print("pto:", pfo)

            criteria[ci + 3] = pfo

            # print("ci", ci)
            for i in range(len(self._objectives)):
                if criteria[ci + i]:
                    score += 1
                else:
                    score += Criteria.weights[i]
                    self._objectives[i] += 1 if Criteria.weights[i] > 0 else 2
            ci += len(Criteria.weights)

        # calculate fitness value based on score
        # print("len items", len(items))
        # print(type(items))
        # print("len objectives:", len(self._objectives))
        # print("score:", score)
        # print("len criteria:", len(criteria))
        # print("fitness: ", score / len(criteria))
        # print("----")
        self._fitness = score / len(criteria)
    
    def dominates(self, other):
        better = False
        for f, obj in enumerate(self.objectives):
            if obj > other.objectives[f]:
                return False

            if obj < other.objectives[f]:
                better = True

        return better




    @property
    def configuration(self):
        return self._configuration

    @property
    def fitness(self):
        return self._fitness

    @property
    def slots(self):
        return self._slots

    @property
    def sections_table(self):
        return self._sections_table

    @property
    def criteria(self):
        return self._criteria

    @property
    def diversity(self):
        return self._diversity

    @property
    def rank(self):
        return self._rank

    @property
    def objectives(self):
        return self._objectives

    @property
    def converted_objectives(self):
        return self._converted_objectives
    
    

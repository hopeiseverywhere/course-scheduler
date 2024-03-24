import random
from typing import Dict, List, Set, Tuple
import numpy as np
from random import randrange
from model import Constant
from model.Criteria import Criteria
from model.Reservation import Reservation
from model.Section import Section
from model.Configuration import Configuration


class Schedule:
    """
    Schedule chromosome
    """
    DAY_NUM, DAY_SLOTS = Constant.DAYS_NUM, Constant.DAY_SLOTS

    def __init__(self, configuration: Configuration):
        self._configuration = configuration
        # Fitness value of chromosome
        self._fitness = 0

        # Time-space slots, one entry represent one time segmentation in one classroom
        slots_length = (Schedule.DAY_NUM * Schedule.DAY_SLOTS
                        * self._configuration.number_of_rooms)
        self._slots: List[List[Section]] = [[] for _ in range(slots_length)]
        # number of sections
        self.size = configuration.number_of_sections
        # number of lab sections
        self.lab_size = configuration.number_of_lab_sections
        # number of criteria
        self.criteria_size = Criteria.criteria_size
        # Section table for chromosome
        # Used to determine first time-space slot used by sections
        # key: Section
        # value: reservation index
        self._sections_table: Dict[Section, int] = {}

        # Flags of section requirements satisfaction
        self._criteria = np.zeros(
            self._configuration.number_of_sections * self.criteria_size,
            dtype=bool)

        self.final_criteria: List[List[bool]] = []

        # Initialize diversity value to 0
        self._diversity = 0.0
        # Initialize rank value to 0
        self._rank = 0
        # Initialize converted objectives list
        self._converted_objectives: list[Schedule] = []
        # Initialize objectives list
        self._objectives: List[int] = []

        # Testing vars
        self._score = 0
        self._criteria_len = len(self._criteria)

    def __str__(self):
        pass

    def copy(self, other: 'Schedule', setup_only: bool):
        if setup_only:
            # print("Set up only = True")
            return Schedule(other.configuration)
        if not setup_only:
            # print("Set up only = False")
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

    def rand_day(self, section: Section) -> int:
        """
        Make a random selection of (day)
        """
        # if the current section is a lab
        # random select day based on its main course

        day = random.choice(section.pref_days)
        if section.is_lab:
            main_course = self._configuration.get_main_section(
                section)
            while abs(day == main_course.day):
                #print("a here: ", section.course_num, section.prof_name, day, main_course.day)

                day = random.choice(section.pref_days)
                if abs(day - main_course.day >= 1):
                    return day
                if abs(day - main_course.day) < 1:
                    self.configuration.clean_room_slot(main_course)
                    conflict_day = random.choice(main_course.pref_days)
                    main_course.set_day(conflict_day)
                    self.configuration.set_room_slot(
                        main_course.room_id, conflict_day, main_course.relative_start, main_course.duration)
                    if abs(day - main_course.day >= 1):
                        return day

        return day

    def rand_time(self, section: Section) -> int:
        """
        Make a random selection of a relative start time
        """
        
        pref_range = section.pref_time_range
        duration = section.duration
        
        if duration > pref_range[1]:
            # for professor only prefer morning time slot
            seed = randrange(2, 4)
            # start_time = randrange(pref_range[0], pref_range[1] + seed)
            start_time = randrange(pref_range[0], pref_range[0] + seed)
        else:
            start_time = randrange(pref_range[0], pref_range[1] + 1 - duration)
        
        # actively assign those who is ok with evening sections evening first
        seed = randrange(2)
        if "evening" in section.pref_time and seed == 1:
            start_time = pref_range[1] - duration

        return start_time

    def check_conflict(self, section: Section):

        # make sure no conflict with its conflict section
        # if section in self.configuration.conflicts_dict.keys():
        day = self.rand_day(section)
        time = self.rand_time(section)
        for conflict in self.configuration.conflicts_dict[section]:
            while Criteria.is_time_and_day_overlap(section, conflict):
                #print("b here")
                day = self.rand_day(section)
                time = self.rand_time(section)
                if (day == conflict.day):
                    conflict_day = random.choice(conflict.pref_days)
                    conflict_time = self.rand_time(conflict)
                    conflict.set_day_and_time(conflict_day, conflict_time)

            return day, time

    def random_selection(self, section: Section):
        """
        Make random selection of (day, time, room_id) from a give section
        :param section:
        :return: tuple (day, start_time, room_id)
        """
        self.configuration.clean_room_slot(section)
        dur = section.duration

        number_of_students = section.number_of_students
        number_of_students = Configuration.round_down_to_nearest_five(
            number_of_students)

        day = self.rand_day(section)
        start_time = self.rand_time(section)
        # select a room with enough size and empty
        room_id = random.choice(
            self._configuration.rooms_by_capacity[number_of_students])
        while self.configuration.is_room_occupied(room_id, day, start_time):
            # print("here")
            room_id = random.choice(
                self._configuration.rooms_by_capacity[number_of_students])
            # if section has a avoid concurrent section
            if self.configuration.is_section_in_concurrent(section):
                day, start_time = self.check_conflict(section)
            else:
                day = self.rand_day(section)
                start_time = self.rand_time(section)

        self.configuration.set_room_slot(room_id, day, start_time, dur)
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
            dur = section.duration
            day, start_time, room_id = self.random_selection(section)
            section.set_all(day, start_time, room_id, dur)
            reservation = Reservation.get_reservation(
                number_of_rooms, day, start_time, room_id)

            # if positions is not None:
            #     positions.append(day)  # day
            #     positions.append(room_id)  # room id
            #     positions.append(start_time)  # stat time

            reservation_index = hash(reservation)
            # fill time space slots for each hour of sections
            for i in range(section.duration - 1, -1, -1):
                new_chromosome_slots[reservation_index + i].append(section)
            # insert in section table of chromosome
            new_chromosome_sections_table[section] = reservation_index
        new_chromosome.get_fitness()

        return new_chromosome

    # def crossover1(self, parent: 'Schedule', number_of_crossover_points,
    #                crossover_prob):
    #     """
    #     Performs crossover operation using to
    #     chromosomes and returns pointer to offspring
    #     :param parent:
    #     :param number_of_crossover_points:
    #     :param crossover_prob:
    #     :return:
    #     """
    #     # check probability of crossover operation
    #     if randrange(100) > crossover_prob:
    #         # no crossover, just copy first parent
    #         return self.copy(self, False)
    #
    #     # new chromosome object, copy chromosome setup
    #     offspring: Schedule = self.copy(self, True)
    #     offspring_sections_table, offspring_slots = (
    #         offspring._sections_table, offspring._slots)
    #
    #     sections_table = self._sections_table
    #     course_sections = tuple(sections_table.keys())
    #     parent_sections_table = parent.sections_table
    #     parent_sections = tuple(parent.sections_table.keys())
    #
    #     # number of sections
    #     size = self.size
    #
    #     cp = size * [False]
    #
    #     # determine crossover point (randomly)
    #     for i in range(number_of_crossover_points, 0, -1):
    #         check_point = False
    #         while not check_point:
    #             p = randrange(size)
    #             if not cp[p]:
    #                 cp[p] = check_point = True
    #
    #     # make new code by combining parent codes
    #     first = randrange(2) == 0
    #
    #     for i in range(size):
    #         if first:
    #             selected_section = course_sections[i]
    #             reservation_index = sections_table[selected_section]
    #             # insert section from first parent
    #             # into new chromosome's class table
    #         else:
    #             selected_section = parent_sections[i]
    #             reservation_index = parent_sections_table[selected_section]
    #             # insert section from second parent
    #             # into new chromosome's class table
    #
    #         dur = selected_section.duration
    #         offspring_sections_table[selected_section] = reservation_index
    #         # all time-space slots of class are copied
    #         for j in range(dur - 1, -1, -1):
    #             offspring_slots[reservation_index + j].append(
    #                 selected_section)
    #
    #         # crossover point
    #         if cp[i]:
    #             # change source chromosome
    #             first = not first
    #
    #     offspring.get_fitness()
    #
    #     # return smart pointer to offspring
    #     return offspring

    def crossover(self, parent: 'Schedule', number_of_crossover_points,
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
        offspring: Schedule = self.copy(self, True)
        offspring_sections_table, offspring_slots = (
            offspring._sections_table, offspring._slots)

        sections_table = self._sections_table
        course_sections = tuple(sections_table.keys())
        parent_sections_table = parent.sections_table
        parent_sections = tuple(parent.sections_table.keys())

        # number of sections
        size = self.size

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
        appeared: Set[int] = set()
        for i in range(0, size):
            selected_section = None
            reservation_index = None
            if first:
                selected_section = course_sections[i]
                reservation_index = sections_table[selected_section]
                # insert section from first parent
                # into new chromosome's class table

            else:
                selected_section = parent_sections[i]
                reservation_index = parent_sections_table[selected_section]
                # insert section from second parent
                # into new chromosome's class table

            dur = selected_section.duration
            offspring_sections_table[selected_section] = reservation_index
            appeared.add(selected_section.section_id)
            # all time-space slots of class are copied
            for j in range(dur - 1, -1, -1):
                offspring_slots[reservation_index + j].append(
                    selected_section)

            self.repair_crossover(appeared, selected_section, offspring_slots)

            # crossover point
            if cp[i]:
                # change source chromosome
                first = not first

        offspring.get_fitness()

        # return smart pointer to offspring
        return offspring

    def repair_crossover(self, appeared: Set[int], section: Section,
                         slots: List[List[Section]]):
        if section.section_id in appeared:
            return None
        number_of_rooms = self._configuration.number_of_rooms
        # if the section is lab, get the main
        if section.is_lab:
            linked = self.configuration.get_main_section(section)
        else:
            linked = self.configuration.get_lab_section(section)

        if linked is not None and linked.section_id not in appeared:
            appeared.add(linked.section_id)
            dur = linked.duration
            day, start_time, room_id = self.random_selection(linked)
            reservation = Reservation.get_reservation(number_of_rooms, day,
                                                      start_time,
                                                      room_id)
            reservation_idx = hash(reservation)
            for j in range(dur):
                slots[reservation_idx + j].append(linked)

        # now check if curr section has conflict
        if section in self.configuration.conflicts_dict.keys():
            for conflict in self.configuration.conflicts_dict[section]:
                if conflict not in appeared:
                    appeared.add(conflict.section_id)
                    dur = conflict.duration
                    day, start_time, room_id = self.random_selection(conflict)
                    reservation = Reservation.get_reservation(number_of_rooms,
                                                              day,
                                                              start_time,
                                                              room_id)
                    reservation_idx = hash(reservation)
                    for j in range(dur):
                        slots[reservation_idx + j].append(linked)

    def repair(self, section: Section, reservation_idx:
               int, reservation: Reservation):
        # extract relevant prams and constant
        number_of_rooms = self._configuration.number_of_rooms
        # DAY_HOURS, DAYS_NUM = Constant.DAY_SLOTS, Constant.DAYS_NUM
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
            section.set_all(day, start_time, room_id, dur)

            reservation = Reservation.get_reservation(number_of_rooms, day,
                                                      start_time,
                                                      room_id)
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
        number_of_sections = self.size
        course_sections = tuple(sections_table.keys())

        # move selected number of sections at random position
        for _i in range(mutation_size, 0, -1):
            # select random chromosome for movement
            move_pos = randrange(number_of_sections)

            # current time-space slot used by class
            if move_pos < len(course_sections):
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
        day_size = Schedule.DAY_SLOTS * number_of_rooms

        ci = 0
        get_room_by_id = configuration.get_room_by_id
        room_by_time_slot = configuration.room_by_time_slot

        # check criteria cna calculate scores for each section in schedule
        for section, reservation_index in items:
            section_score = 0
            reservation = Reservation.parse(reservation_index)

            # coordinates of time-space slot
            day, time, room = (reservation.day,
                               reservation.time, reservation.room_id)

            dur = section.duration
            section_id = section.section_id

            # 1. check room overlapping
            room_overlapping = Criteria.is_room_overlapped(
                room_by_time_slot, room, day, time)

            criteria[ci + 0] = not room_overlapping

            # 2. does curr room have enough seats
            room = get_room_by_id(room)
            enough_seats = Criteria.is_seat_enough(room, section)
            criteria[ci + 1] = enough_seats

            # 3. is professor overlap
            time_id = day * day_size + time
            prof_overlap = Criteria.is_prof_overlapped(slots, section,
                                                       number_of_rooms, time_id)
            criteria[ci + 2] = not prof_overlap

            # 4. if professor preference time satisfied
            # both are relative time
            start_time = time
            end_time = start_time + dur

            prof_satisfied = Criteria.is_prof_satisfied(section.pref_time_range,
                                                        start_time,
                                                        end_time)
            criteria[ci + 3] = prof_satisfied

            # 5. Check lab conditions met
            # lab_timing = Criteria.is_lab_satisfied(
            # section, self._sections_table)
            if section.is_lab:
                lab_timing = (
                    Criteria.is_lab_satisfied(section,
                                              configuration.get_main_section(
                                                  section)))
                criteria[ci + 4] = lab_timing
            else:
                criteria[ci + 4] = True

            # 6. Check concurrent courses
            conflict = (
                Criteria.is_conflict(section, configuration.conflicts_dict))
            criteria[ci + 5] = not conflict

            # 7. Check day satisfied
            do = Criteria.is_day_satisfied(section.pref_days, day)
            criteria[ci + 6] = do

            # if the constraint checks out, ci[i] must be true
            for i in range(len(self._objectives)):
                if criteria[ci + i]:  # Checking if that criteria was fulfilled
                    score += 1
                else:
                    score += Criteria.weights[i]  # Adding partial credit for that weight if unfulfilled
                    self._objectives[i] += 1 if Criteria.weights[i] > 0 else 2
            ci += self.criteria_size

        # calculate fitness value based on score
        self._fitness = score / len(criteria)
        self._score = score

    def __eq__(self, other):
        if isinstance(other, Schedule):
            return self.fitness == other.fitness
        return False

    def __lt__(self, other):
        if isinstance(other, Schedule):
            return self.fitness < other.fitness
        raise TypeError("Cannot compare CustomObject with non-CustomObject")

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
        # print(self._objectives)
        return self._objectives

    @property
    def converted_objectives(self):
        # print(self._converted_objectives)
        return self._converted_objectives

    @property
    def score(self):
        return self._score

    @property
    def criteria_length(self):
        return self._criteria_len

    def print_criteria(self):
        size = self.criteria_size
        num = 0
        for i in range(0, len(self.criteria), size):
            print(num, ":", self.criteria[i:i + size])
            num += 1
        

    def update_final_criteria(self):
        size = self.criteria_size
        
        self.final_criteria = self.criteria.reshape(-1, size).tolist()
        # print(self.final_criteria)
        # num = 0
        # for lis in self.final_criteria:
        #     print(num, ":", lis)
        #     num += 1

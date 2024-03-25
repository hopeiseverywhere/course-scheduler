from model import Constant
from model.Room import Room
from model.Section import Section
from typing import Dict, List, Any, Set


class Configuration:
    """Reads configuration file and stores parsed objects"""

    def __init__(self):
        # Indicate that configuration is not parsed yet
        self._isEmpty = True
        # parsed rooms object
        # key: room id
        # value: room object
        self._rooms = {}
        # key: section id
        # value: section object
        self._sections_by_id = {}
        # key: capacity, range from 5 to 100 inclusive, increment by 5
        # value: a list of rooms that can >= key
        self.rooms_by_capacity = {}

        # key : room id
        # values = [6 days]:[all time slots]
        self.room_by_time_slot: Dict[int, Dict[int, List[bool | int]]] = {}
        # parsed sections
        self._sections = []

        # key lab section : value main course section
        self.lab_main_course_sec: Dict[Section: Section] = {}
        # map lan/main to main/lab
        self.lab_and_main_secs: Dict[Section: Section] = {}

        # lab section id : main section id
        self.lab_main_course_id: Dict[int: int] = {}

        # avoid concurrent courses
        self.conflicts_dict: Dict[Section: List[Section]] = {}

    def clear_data(self):
        """Clears all previous data stored in the Configuration object."""
        self._isEmpty = True
        self._rooms = {}
        self._sections_by_id = {}
        self.rooms_by_capacity = {}
        self._sections = []
        Room.restart_id()
        Section.restart_id()

    def update_preference_range(self):
        """convert prof's preference from string to a relative time range"""
        for section in self._sections:
            prof_preference = section.pref_time
            time_range = []
            start = (Constant.time_ranges.get(prof_preference[0])[0])
            end = (Constant.time_ranges.get(prof_preference[-1])[1])
            time_range.append(start)
            time_range.append(end)
            section.pref_time_range = time_range
            # print(section.pref_time_range)

    def parse_file(self, data: List[Dict[str, Any]]) -> None:
        """
        Parses file data to populate the configuration.
        """

        if self._isEmpty is False:
            raise ValueError(
                "Configuration is already initialized. "
                "Clear previous data before processing new data.")
        Room.restart_id()
        Section.restart_id()
        self._rooms = {}
        self._sections = []

        for item in data:
            if 'room' in item:
                
                room_data = item['room']
                room = Room(
                    name=room_data['name'],
                    number_of_seats=room_data['size']
                )
                self._rooms[room.id] = room
                # update room by time slot
                self.room_by_time_slot[room.id] = {}
                for i in range(Constant.DAYS_NUM):
                    self.room_by_time_slot[room.id][i] = [
                        False] * Constant.DAY_SLOTS
            elif 'section' in item:
                # print("sth wrong")
                section_data = item['section']
                section = Section(
                    course_num=section_data['course'],
                    course_name="",
                    professor=section_data['professor'],
                    pref_time=section_data['pref_time'],
                    pref_days=section_data['pref_day'],
                    is_lab=section_data.get('is_lab'),
                    duration=int(
                        section_data['duration'] / Constant.TIME_SEGMENT),
                    students=section_data['students']
                )
                # print(section_data['duration'] / Constant.TIME_SEGMENT)
                self._sections.append(section)
                self._sections_by_id[section.section_id] = section

        # self._sections = sorted(self._sections, key=lambda x: x.is_lab)
        # #  test out put -----------------------
        # for section in self.sections:
        #     print("{:<20} {}".format(section.to_str(), section.is_lab))
        # print()
        # print(self)

        self.update_preference_range()
        self.init_room_by_capacity()
        self.init_lab_section_dict()
        self.init_non_concurrent_dict()
        self._isEmpty = False
        # print(self.room_by_time_slot[0])

    def init_room_by_capacity(self):
        """
        init the dictionary with keys ranging from 5 to 100
        """
        self.rooms_by_capacity = {key: [] for key in range(5, 101, 5)}
        for room in self._rooms.values():
            capacity = room.number_of_seats
            for i in range(5, 101, 5):
                if capacity >= i:
                    self.rooms_by_capacity[i].append(room.id)

        # print(self.rooms_by_capacity)

    def init_lab_section_dict(self):
        """lab section : main section
        """
        lab_set: Set[int] = set()
        main_set: Set[int] = set()
        # load from constant
        for key in Constant.lab_main_courses.keys():
            for lab in self.sections:
                if lab.course_num == key and lab.section_id not in lab_set:
                    lab_set.add(lab)
                    self.lab_main_course_sec[lab] = None
                    self.lab_main_course_id[lab.section_id] = None

        # print(self.lab_main_course)
        for lab in self.lab_main_course_sec.keys():
            for section in self.sections:
                if (section.prof_name == lab.prof_name and
                    Constant.lab_main_courses[
                        lab.course_num] == section.course_num and
                        section.section_id not in main_set):
                    main_set.add(section)
                    self.lab_main_course_sec[lab] = section
                    self.lab_main_course_id[lab.section_id] = section.section_id

                    continue

        main_sec_to_lab: Dict[Section, Section] = {}
        # map main section to lab
        for key, item in self.lab_main_course_sec.items():
            main_sec_to_lab[item] = key

        # join 2 dictionaries together
        self.lab_and_main_secs = main_sec_to_lab.copy()
        self.lab_and_main_secs.update(self.lab_main_course_sec)

    def init_non_concurrent_dict(self):
        """
        Map a course to its conflict courses
        """
        for section in self.sections:
            if section.course_num in Constant.concurrent_courses.keys():
                self.conflicts_dict[section] = []

        for section in self.conflicts_dict.keys():
            for other_section in self.sections:
                if other_section.course_num == Constant.concurrent_courses[
                        section.course_num]:
                    self.conflicts_dict[section].append(other_section)

        # test out put ------------------
        # print("{:<10} {}".format("Main course", "Conflicts"))
        # for key, value_list in self.conflicts_dict.items():
        #     key_sections = key.course_name
        #     value_sections = [value.course_name for value in value_list]
        #     print("{:<10} : {}".format(key_sections, value_sections))

    def get_main_section(self, lab: Section):
        """
        Given a lab section, return the corresponding main section
        """
        if lab in self.lab_main_course_sec.keys():
            return self.lab_main_course_sec[lab]

    def get_lab_section(self, main_sec: Section):
        """
        Given a lab section, return the corresponding lab section
        """
        for lab, main_course in self.lab_main_course_sec.items():
            if main_course == main_sec:
                return lab
        return None

    def get_main_section_by_id(self, lab_id: int):
        """
        Given a lab section id, return the corresponding main section
        """
        if lab_id in self.lab_main_course_id.keys():
            main_sec_id = self.lab_main_course_id[lab_id]
            return self.get_section_by_id(main_sec_id)
        return None

    def get_linked_section(self, sec: Section):
        """Given a lab/main section, return the corresponding main/lab section

        Args:
            sec (Section): _description_
        """
        if sec in self.lab_and_main_secs:
            return self.lab_and_main_secs.get(sec)
        return False

    def get_room_by_id(self, room_id: int) -> Room | None:
        """
        Return room object with a specific id, return None otherwise
        """
        if room_id in self._rooms:
            return self._rooms.get(room_id)
        return None

    def get_section_by_id(self, section_id: int) -> Section | None:
        """
        Return section with a specific id, return None otherwise
        """
        if section_id in self._sections_by_id:
            return self._sections_by_id.get(section_id)
        return None

    def is_room_occupied(self, sec_id: int, dur: int,  day: int,
                         relative_time: int, room_id: int) -> bool:
        """Given room id and a relative start time,
        check whether the room is occupied

        Args:
            room_id (int): _description_
            relative_time (int): _description_

        Returns:
            bool: _description_
        """
        sublist = []
        for i in range(relative_time, relative_time + dur):
            sublist.append(self.room_by_time_slot[room_id][day][i])
        if all(el is False for el in sublist):
            # Condition 1: All elements are False -> room is not occupied
            return False

        count_false = 0
        count_id = 0
        for el in sublist:
            if el is False:
                count_false += 1
            elif el == sec_id:
                count_id += 1
            elif el is not False and el != sec_id:
                # Condition 2: If any element is not equal to sec_id and not false, room is occupied
                return True
        # Condition 3: If false count + section count == length of sublist -> room is not occupied
        if count_false + count_id == len(sublist):
            return False

        # Condition 2: If any element is not equal to sec_id, room is occupied
        return any(el != sec_id for el in sublist)

    def is_section_linked_to_lab(self, section: Section) -> bool:
        """Given a section, check whether it linked to a lab/main section

        Args:
            section (Section): _description_

        Returns:
            bool: _description_
        """
        if section in self.lab_and_main_secs:
            return True
        return False

    def is_section_in_concurrent(self, section: Section) -> bool:
        if self.conflicts_dict.get(section) is not None:
            return True
        return False

    def set_room_slot(self, sec_id: int, room_id: int, day: int, relative_start: int,
                      dur: int):
        """If a section randomly select day, time and room, make that room occupied

        Args:
            room_id (int): _description_
            day (int): _description_
            relative_start (int): _description_
            dur (int): _description_
        """
        sublist = []
        for i in range(relative_start, relative_start + dur):
            sublist.append(self.room_by_time_slot[room_id][day][i])
        
        if self.is_room_occupied(sec_id=sec_id, dur=dur, day=day, relative_time=relative_start, room_id=room_id) is False:
            for i in range(relative_start, relative_start + dur):

                self.room_by_time_slot[room_id][day][i] = sec_id
            self.sections[sec_id].set_all(day, relative_start, room_id)

    def clean_room_slot(self, section: Section):
        """Clean the previous selection

        Args:
            section (Section): _description_
        """

        if section.room_id is not None and section.relative_start is not None:

            day = section.day
            room_id = section.room_id
            dur = section.duration
            relative_start = section.relative_start
            sec_id = section.section_id

            for i in range(relative_start, relative_start + dur):
                # only clean the slot with current section id
                curr = self.room_by_time_slot[room_id][day][i]
                if curr == sec_id:
                    self.room_by_time_slot[room_id][day][i] = False
            # self.print_room_slot("clean room",room_id, day)

    def print_room_slot(self, msg: str, room_id: int, day: int):
        print(msg, room_id, self.room_by_time_slot[room_id][day])

    @staticmethod
    def round_down_to_nearest_five(number: int) -> int:
        """Rounds down the given number to the nearest multiple of 5.
        Args:
            number (int): The number to round down
        Returns:
            int: The rounded down number to the nearest multiple of 5
        """
        return (number // 5) * 5

    @staticmethod
    def print_dict(dict: Dict[Section, Section]):
        """
        print a dictionary for testing
        """
        print("{:<20} {}".format("A section", "Mapped Section"))
        for sec1, sec2 in dict.items():
            print(
                "{:<20} {}".format(sec1.course_num + "+" + str(sec1.section_id),
                                   sec2.course_num + "+" + str(
                                       sec2.section_id)))

    def __str__(self) -> str:
        info = f"Number of Rooms: {self.number_of_rooms}\n"
        info += f"Number of Sections: {self.number_of_sections}\n"
        return info

    @property
    def number_of_sections(self):
        return len(self._sections)

    @property
    def number_of_rooms(self):
        return len(self._rooms)

    @property
    def sections(self):
        return self._sections

    @property
    def number_of_lab_sections(self):
        return len(self.lab_main_course_id.keys())

    def print_room_slot(self):
        """Print room mapped to day, time slot map
        """
        day_mapping = {0: 'MON', 1: 'TUW', 2: 'WED', 3: 'THU', 4: 'FRI', 5: 'SAT'}
        for room_id, room_data in self.room_by_time_slot.items():
            room_name = self.get_room_by_id(room_id)
            print(f"Room: {room_name}")
            for day, time_slots in room_data.items():
                print(f"  Day: {day_mapping[day]}")
                print("    Time Slots:", time_slots)

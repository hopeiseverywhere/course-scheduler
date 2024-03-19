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
        # parsed sections
        self._sections = []
        # key lab section : value main course section
        self.lab_main_course_sec: Dict[Section: Section] = {}
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
            # print(section.Preference_range)

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

    def parse_file(self, data: list[dict[str, Any]]) -> None:
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
            elif 'section' in item:
                section_data = item['section']
                section = Section(
                    course=section_data['course'],
                    professor=section_data['professor'],
                    pref_time=section_data['pref_time'],
                    is_lab=section_data.get('is_lab'),
                    duration=int(
                        section_data['duration'] / Constant.TIME_SEGMENT),
                    students=section_data['students']
                )
                self._sections.append(section)
                self._sections_by_id[section.section_id] = section

        self._sections = sorted(self._sections, key=lambda x: x.is_lab)
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

    def init_lab_section_dict(self):
        """lab section : main section
        """
        lab_set: Set[int] = set()
        main_set: Set[int] = set()
        # load from constant
        for key in Constant.lab_main_courses.keys():
            for lab in self.sections:
                if lab.course_name == key and lab.section_id not in lab_set:
                    lab_set.add(lab)
                    self.lab_main_course_sec[lab] = None
                    self.lab_main_course_id[lab.section_id] = None

        # print(self.lab_main_course)
        for lab in self.lab_main_course_sec.keys():
            for section in self.sections:
                if (section.prof_name == lab.prof_name and
                    Constant.lab_main_courses[
                        lab.course_name] == section.course_name and
                        section.section_id not in main_set):
                    main_set.add(section)
                    self.lab_main_course_sec[lab] = section
                    self.lab_main_course_id[lab.section_id] = section.section_id

                    continue

        # test out put ------------------
        # print("{:<20} {}".format("Lab section", "Main section"))
        # for lab in self.lab_main_course_sec.keys():
        #     print("{:<20} {}".format(lab.to_str(),
        #                              self.lab_main_course_sec[lab].to_str()))
        # for lab_id in self.lab_main_course_id.keys():
        #     print("{:<20} {}".format(lab_id, self.lab_main_course_id[lab_id]))

    def print_lab_section_dict(self):
        print("{:<20} {}".format("Main section", "Day time"))
        for lab, main_course in self.lab_main_course_sec.items():
            print("{:<20} {} {}".format(main_course.course_name,
                                        main_course.day,
                                        main_course.start_time))

    def init_non_concurrent_dict(self):
        """
        Map a course to its conflict courses
        """
        for section in self.sections:
            if section.course_name in Constant.concurrent_courses.keys():
                self.conflicts_dict[section] = []

        for section in self.conflicts_dict.keys():
            for other_section in self.sections:
                if other_section.course_name == Constant.concurrent_courses[section.course_name]:
                    self.conflicts_dict[section].append(other_section)

        # test out put ------------------
        # print("{:<10} {}".format("Main course", "Conflicts"))
        # for key, value_list in self.conflicts_dict.items():
        #     key_sections = key.course_name
        #     value_sections = [value.course_name for value in value_list]
        #     print("{:<10} : {}".format(key_sections, value_sections))

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

    @staticmethod
    def round_down_to_nearest_five(number: int) -> int:
        """Rounds down the given number to the nearest multiple of 5.
        Args:
            number (int): The number to round down
        Returns:
            int: The rounded down number to the nearest multiple of 5
        """
        return (number // 5) * 5

    def __str__(self) -> str:
        info = f"Number of Rooms: {self.number_of_rooms}\n"
        info += f"Number of Sections: {self.number_of_sections}\n"
        return info

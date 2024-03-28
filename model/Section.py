import random
from random import randrange
from model import Constant
from util import utility

class Section:
    # ID counter used to assign IDs automatically
    _next_section_id = 0

    # Initializes class object
    def __init__(self, course_num: str, course_name: str, professor: str, pref_time: list[str], pref_days: list[int], is_lab: bool, duration: int, students: int):
        self.section_id = Section._next_section_id
        Section._next_section_id += 1
        # Course number
        self.course_num = course_num
        self.course_name = course_name
        # Return pointer to professor who teaches
        self.prof_name = professor
        # Professor's preference
        self.pref_time = pref_time
        # Professor's preference time range
        self.pref_time_range: list[int] = []
        self.pref_days = pref_days
        # Returns number of seats (students) required in room
        self.number_of_students = students
        # Returns True if the section is a lab, false otherwise
        self.is_lab = is_lab
        # Returns duration of class in hours
        self.duration = duration

        # Section's day
        self.day = None
        # Section's start time
        self.start_time = None
        # Section's end time
        self.end_time = None
        # Section's room's id
        self.room_id = None
        # Section's relative start time
        self.relative_start = None
        # Whether all criteria satisfied for the section
        self.criteria_met = False

    def assign_time(self):
        # Randomly select a start time from available times
        self.start_time = randrange(
            self.pref_time_range[0] + self.duration,
            self.pref_time_range[1] - self.duration)

    def assign_day(self):
        self.day = randrange(Constant.DAYS_NUM)

    def section_overlaps(self, other: 'Section'):
        """Return true if 2 section's time overlaps

        """
        if self.day != other.day or self.section_id == other.section_id:
            return False
        if self.relative_start is None or other.relative_start is None:
            return False
        curr_start = self.relative_start
        curr_end = self.relative_start
        comp_start = other.relative_start
        comp_end = other.relative_start
        return (comp_start <= curr_start <= comp_end or
                comp_start <= curr_end <= comp_end)
        

    
    def professor_overlaps(self, other: 'Section'):
        """Returns True if another section has same professor at same time
        """
        if self.section_id != other.section_id and self.section_overlaps(other):
            return self.prof_name == other.prof_name

    def __hash__(self):
        return hash(self.section_id)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return hash(self) == hash(other)

    def __ne__(self, other):
        # Not strictly necessary, but to avoid having both x==y and x!=y
        # True at the same time
        return not (self == other)

    def __str__(self):
        return (f"Section ID: {self.section_id}, "
                f"Course: {self.course_num}, "
                f"Professor: {self.prof_name}, "
                f"Preference: {self.pref_time}, "
                f"Lab Section: {self.is_lab}, "
                f"Duration: {self.duration}, "
                f"Start Day: {self.day}, "
                f"Start Time: {self.start_time}, "
                f"Room: {self.room_id}, "
                f"Relative Start: {self.relative_start}, "
                f"Criteria Satisfied: {self.criteria_met}")

    def set_day(self, day):
        self.day = day
    
    def set_day_and_time(self, day, time):
        self.day = day
        self.relative_start = time

    def set_all(self, day, time, room_id):
        """
        Set day, time, room to a section that has finished random generation
        :param day:
        :param time: relative time slot in 20-minute segmentation
        :param room_name:
        :return:
        """
        self.day = day
        self.relative_start = time
        self.room_id = room_id

    def set_criteria_met(self, criteria_met):
        self.criteria_met = criteria_met

    def set_actual_time(self):
        # convert relative time to actual time
        self.start_time = self.time_slot_to_real_time(self.relative_start)
        self.end_time = self.time_slot_to_real_time(
            self.relative_start + self.duration)

    def to_str(self):
        return self.course_num + " " + self.prof_name

    def is_lab_section(self):
        """
        check if current section is a lab section
        """
        if self.is_lab:
            return True
        return False

    # Restarts ID assignments
    @staticmethod
    def restart_id() -> None:
        Section._next_section_id = 0

    @staticmethod
    def set_room(self, room_id):
        self.room_id = room_id

    @staticmethod
    def set_start_day(self, day):
        self.day = day

    @staticmethod
    def set_start_time(self, time):
        self.start_time = time

    @staticmethod
    def time_slot_to_real_time(slot):
        # get total minutes
        total_minutes = slot * Constant.TIME_SEGMENT + Constant.DAY_START_HOUR * \
                        Constant.HOUR_TO_MINUTES + Constant.DAY_START_MINUTES
        # get hour
        hours = total_minutes // 60
        # get minutes
        minutes = total_minutes % 60
        return f"{hours:02d}:{minutes:02d}"

    @staticmethod
    def section_to_dict(section):
        return {
            "Section Id": section.section_id,
            "Course": section.course_num,
            "Prof": section.prof_name,
            "Start Day": utility.dayStrConverter(section.day),
            "Start Time": section.start_time,
            "End Time": section.end_time,
            "Room": section.room_id,
            "Dur": section.duration * Constant.TIME_SEGMENT,
            "Relative Start": section.relative_start,
            "Criteria Satisfied": section.criteria_met
        }

import random
from random import randrange
from model import Constant

class Section:
    # ID counter used to assign IDs automatically
    _next_section_id = 0

    # Initializes class object
    def __init__(self, course: str, professor: str, pref_time: list[str],
        requires_lab: bool, duration: int, students: int):
        self.section_id = Section._next_section_id
        Section._next_section_id += 1
        # Course name
        self.course_name = course
        # Return pointer to professor who teaches
        self.prof_name = professor
        # Professor's preference
        self.pref_time = pref_time
        # Professor's preference time range
        self.pref_time_range = []
        # Returns number of seats (students) required in room
        self.number_of_students = students
        # Returns TRUE if class requires a lab
        self.lab_required = requires_lab
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
        self.relative_start = None



    def assign_time(self):
        # Randomly select a start time from available times
        self.start_time = randrange(self.pref_time_range[0] + self.duration
                                    , self.pref_time_range[1] - self.duration)

    def assign_day(self):
        self.day = randrange(Constant.DAYS_NUM)

    # Returns TRUE if another section has same professor at same time
    def professor_overlaps(self, other: 'Section'):
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
                f"Course: {self.course_name}, "
                f"Professor: {self.prof_name}, "
                f"Preference: {self.pref_time}, "
                f"Requires Lab: {self.lab_required}, "
                f"Duration: {self.duration}, "
                f"Start Day: {self.day}, "
                f"Start Time: {self.start_time}, "
                f"Room: {self.room_id}, "
                f"Relative Start: {self.relative_start}")


    # Restarts ID assignments
    @staticmethod
    def restart_ids() -> None:
        Section._next_section_id = 0

    @staticmethod
    def set_room(self, room_name):
        self.room_id = room_name

    @staticmethod
    def set_start_day(self, day):
        self.day = day

    @staticmethod
    def set_start_time(self, time):
        self.start_time = time

    @staticmethod
    def time_slot_to_real_time(slot):
        # get total minutes
        total_minutes = slot * Constant.TIME_SEGMENT + Constant.DAY_START_HOUR * Constant.HOUR_TO_MINUTES + Constant.DAY_START_MINUTES
        # get hour
        hours = total_minutes // 60
        # get minutes
        minutes = total_minutes % 60
        return f"{hours:02d}:{minutes:02d}"

    def set_all(self, day, time, room_name, duration):
        """
        Set day, time, room to a section that has finished random generation
        :param day:
        :param time: relative time slot in 20-minute segmentation
        :param room_name:
        :return:
        """
        self.day = day
        self.relative_start = time
        # convert relative time to actual time
        self.start_time = self.time_slot_to_real_time(time)
        self.end_time = self.time_slot_to_real_time(time + duration)
        self.room_id = room_name

    def set_actual_time(self):
        # convert relative time to actual time
        self.start_time = self.time_slot_to_real_time(self.relative_start)
        self.end_time = self.time_slot_to_real_time(self.relative_start + self.duration)
    @staticmethod
    def section_to_dict(section):
        return {
            "Section Id": section.section_id,
            "Course": section.course_name,
            "Prof": section.prof_name,
            "Start Day": section.day,
            "Start Time": section.start_time,
            "End Time": section.end_time,
            "Room": section.room_id,
            "Dur": section.duration,
            "Relative Start": section.relative_start
        }
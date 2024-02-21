import random
from random import randrange

from model import Constant


class Section:
    # ID counter used to assign IDs automatically
    _next_section_id = 0

    # Initializes class object
    def __init__(self, course: str, professor: str, preference: list[str],
        requires_lab: bool, duration: int, students: int):
        self.Id = Section._next_section_id
        Section._next_section_id += 1
        # Course name
        self.Course = course
        # Return pointer to professor who teaches
        self.Professor = professor
        # Professor's preference
        self.Preference = preference
        # Professor's preference range
        self.Preference_range = []
        # Returns number of seats (students) required in room
        self.Number_Of_Seats = students
        # Returns TRUE if class requires a lab
        self.Lab_Required = requires_lab
        # Returns duration of class in hours
        self.Duration = duration

        # Section's day
        self.Day = None
        # Section's start time
        self.Start_Time = None
        # Section's room' id
        self.Room = None

    # def assign_room(self, room_id):
    #     # Randomly select a room from available rooms
    #     self.room = room_id

    def assign_time(self):
        # Randomly select a start time from available times
        self.start_time = randrange(self.Preference_range[0] + self.Duration
                                    , self.Preference_range[1] - self.Duration)

    def assign_day(self):
        self.Day = randrange(Constant.DAYS_NUM)

    # Returns TRUE if another section has same professor at same time
    def professor_overlaps(self, other: 'Section'):
        return self.Professor == other.Professor

    def __hash__(self):
        return hash(self.Id)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return hash(self) == hash(other)

    def __ne__(self, other):
        # Not strictly necessary, but to avoid having both x==y and x!=y
        # True at the same time
        return not (self == other)

    def __str__(self):
        return (f"Section ID: {self.Id}, "
                f"Course: {self.Course}, "
                f"Professor: {self.Professor}, "
                f"Preference: {self.Preference}, "
                f"Requires Lab: {self.Lab_Required}, "
                f"Duration: {self.Duration}, "
                f"Start Day: {self.Day}, "
                f"Start Time: {self.Start_Time}, "
                f"Room: {self.Room}")

    # Restarts ID assignments
    @staticmethod
    def restart_ids() -> None:
        Section._next_section_id = 0

    @staticmethod
    def set_room(self, room_name):
        self.Room = room_name

    @staticmethod
    def set_start_day(self, day):
        self.Day = day

    @staticmethod
    def set_start_time(self, time):
        self.Start_Time = time

    def set_all(self, day, time, room_name):
        self.Day = day
        self.Start_Time = time
        self.Room = room_name

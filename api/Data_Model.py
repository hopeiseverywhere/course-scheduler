from pydantic import BaseModel, validator
from typing import List, Union
from model import Constant
from util import utility

class Section(BaseModel):
    """
    Represents a section.

    Attributes:
        id (int): The unique identifier for the section.
        course (str): The course name associated with the section.
        professor (str): The professor teaching the section.
        pref_time (List[str]): The preferred times for the section, ["Morning", "Afternoon", "Evening"].
        pref_day (List[int]): The preferred days for the section, ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'].
        lab (bool): Indicates whether the section is a lab section or not.
        duration (int): The duration of the section in minutes
        students (int): The number of students enrolled in the section.

    Methods:
        validate_positive_integer(cls, value): Validates that the value is a positive integer.
    """
    course: str
    professor: str
    pref_time: List[str]
    pref_day: List[str]
    is_lab: bool
    duration: int
    students: int

    @validator('duration', 'students', pre=True)
    def validate_positive_integer(cls, value):
        """Validate that the value is a positive integer."""
        if value <= 0:
            raise ValueError('Value must be a positive integer')
        return value
    
    @validator('duration', pre=True)
    def validate_duration(cls, value):
        """Validate that the duration is a positive integer and divisible by the time segment."""
        if value <= 0:
            raise ValueError('Duration must be a positive integer')
        if value % Constant.TIME_SEGMENT != 0:
            raise ValueError(f'Duration must be divisible by current time segment: {Constant.TIME_SEGMENT}')
        return value

    @validator('pref_time')
    def validate_pref_time(cls, value):
        """Validate that pref_time contains only 'morning', 'afternoon', or 'evening'."""
        allowed_times = ["Morning", "Afternoon", "Evening"]
        for time1 in value:
            if time1 not in allowed_times:
                raise ValueError(f"Invalid time '{time1}'. Must be one of: {', '.join(allowed_times)}")
        return value
    
    @validator('pref_day')
    def validate_pref_day(cls, value):
        """Validate that pref_time contains only 0 to 6."""
        allowed_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for day1 in value:
            if day1 not in allowed_days:
                raise ValueError(f"Invalid time '{day1}'. Must be one of: {', '.join(allowed_days)}")
        

        max_day = Constant.DAYS_NUM - 1
        min_day = 0
        
        for day1 in value:
            day2 = utility.dayStrConverter(day1)
            # print(day1)
            if day2 < min_day or day2 > max_day:
                raise ValueError(f"Invalid day '{day1}'. Must between of: {utility.dayStrConverter(min_day)} and {utility.dayStrConverter(max_day)} inclusive")
        return value

class Room(BaseModel):
    """
    Represents a room.

    Attributes:
        name (str): The name or identifier of the room.
        size (int): The capacity or size of the room in terms of seats.

    Methods:
        validate_positive_integer(cls, value): Validates that the value is a positive integer.
    """
    name: str
    size: int

    @validator('size', pre=True)
    def validate_positive_integer(cls, value):
        """Validate that the value is a positive integer."""
        if value <= 0:
            raise ValueError('Value must be a positive integer')
        return value


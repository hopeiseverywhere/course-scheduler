import json
import codecs

from model import Constant
from model.Room import Room
from model.Section import Section


class Configuration:
    """Reads configuration file and stores parsed objects"""

    def __init__(self):
        # Indicate that configuration is not parsed yet
        self._isEmpty = True
        # parsed rooms object
        self._rooms = {}
        # key: capacity, range from 5 to 100 inclusive, increment by 5
        # value: a list of rooms that can >= key
        self.rooms_by_capacity = {}
        # parsed sections
        self._sections = []

    def update_preference_range(self):
        """convert prof's preference from string to a range"""
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
        # init the dictionary with keys ranging from 5 to 100
        self.rooms_by_capacity = {key: [] for key in range(5, 101, 5)}
        for room in self._rooms.values():
            capacity = room.number_of_seats
            for i in range(5, 101, 5):
                if capacity >= i:
                    self.rooms_by_capacity[i].append(room.id)

        # print(self.rooms_by_capacity)

    def parse_file(self, file_name: str) -> None:
        self._rooms = {}
        self._sections = []

        with codecs.open(file_name, "r", "utf-8") as f:
            data = json.load(f)

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
                        requires_lab=section_data['lab'],
                        duration=section_data['duration'],
                        students=section_data['students']
                    )
                    self._sections.append(section)
        self.update_preference_range()
        self.init_room_by_capacity()

    @property
    def number_of_sections(self):
        return len(self._sections)

    @property
    def number_of_rooms(self):
        return len(self._rooms)

    @property
    def sections(self):
        return self._sections

    def get_room_by_id(self, room_id: int) -> Room:
        """
        Return room with specific id, return None otherwise
        :param room_id:
        :return:
        """
        if room_id in self._rooms:
            return self._rooms.get(room_id)
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

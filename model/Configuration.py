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
        # parsed rooms
        self._rooms = {}
        # parsed sections
        self._sections = []

    def update_preference_range(self):
        """convert prof's preference from string to a range"""
        for section in self._sections:
            prof_preference = section.Preference
            range = []
            start = (Constant.time_ranges.get(prof_preference[0])[0])
            end = (Constant.time_ranges.get(prof_preference[-1])[1])
            range.append(start)
            range.append(end)
            section.Preference_range = range
            # print(section.Preference_range)


    def parse_file(self, file_name: str) -> None:
        # clear previously parsed objects
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
                    self._rooms[room.Id] = room
                elif 'section' in item:
                    section_data = item['section']
                    section = Section(
                        course=section_data['course'],
                        professor=section_data['professor'],
                        preference=section_data['preference'],
                        requires_lab=section_data['lab'],
                        duration=section_data['duration'],
                        students=section_data['students']
                    )
                    self._sections.append(section)
        self.update_preference_range()

    @property
    def number_of_sections(self):
        return len(self._sections)

    @property
    def number_of_rooms(self):
        return len(self._rooms)

    @property
    def sections(self):
        return self._sections

    def get_room_by_id(self, id: int) -> Room:
        """
        Return room with specific id, return None otherwise
        :param id:
        :return:
        """
        if id in self._rooms:
            return self._rooms.get(id)
        return None



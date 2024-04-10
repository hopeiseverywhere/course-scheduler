import Section
from typing import List


class Professor:
    """A professor class, not using this right now
    """
    # Initializes professor data
    def __init__(self, prof_id: int, name: str, preference: list[str]):
        self.prof_id = prof_id
        self.name = name
        # stores professor's list of sections to teach
        self.sections = []
        self.pref_time = preference

    # Bind professor to a section
    def add_section_to_teach(self, section: Section):
        self.sections.append(section)

    def __str__(self):
        list_of_sections = ""
        for classes in self.sections:
            list_of_sections += classes
            list_of_sections += " "
        list_of_preferences = ""
        for pref in self.pref_time:
            list_of_preferences += pref
            list_of_sections += " "
        return self.name + ", " + list_of_sections + list_of_preferences

    def __hash__(self):
        return hash(self.prof_id)

    # Compares ID's of two objects which represent professors
    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return hash(self) == hash(other)

    def __ne__(self, other):
        # Not strictly necessary, but to avoid having both x==y and x!=y
        # True at the same time
        return not (self == other)

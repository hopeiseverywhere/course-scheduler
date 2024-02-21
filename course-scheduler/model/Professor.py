import Section


# Stores data about professor
class Professor:
    # Initializes professor data
    def __init__(self, id: int, name: str, preference: list[str]):
        self.Id = id
        self.Name = name
        # stores professor's list of sections to teach
        self.Sections = []
        self.Preference = preference

    # Bind professor to a section
    def add_section_to_teach(self, section: Section):
        self.Sections.append(section)

    def __str__(self):
        list_of_sections = ""
        for classes in self.Sections:
            list_of_sections += classes
            list_of_sections += " "
        list_of_preferences = ""
        for pref in self.Preference:
            list_of_preferences += pref
            list_of_sections += " "
        return self.Name + ", " + list_of_sections + list_of_preferences

    def __hash__(self):
        return hash(self.Id)

    # Compares ID's of two objects which represent professors
    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return hash(self) == hash(other)

    def __ne__(self, other):
        # Not strictly necessary, but to avoid having both x==y and x!=y
        # True at the same time
        return not (self == other)

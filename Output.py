from model.Configuration import Configuration
from model.Schedule import Schedule
def get_result(solution: Schedule):
    configuration = solution.configuration
    number_of_rooms = configuration.number_of_rooms
    get_room_by_id = Configuration.get_room_by_id

    rooms = configuration._rooms
    sections = configuration._sections

    for section in sections:
        if section.room_id is not None:
            print(section)
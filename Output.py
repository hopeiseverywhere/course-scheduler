import json
# from model.Configuration import Configuration
from model.Schedule import Schedule
from model.Section import Section


def get_result(solution: Schedule):
    configuration = solution.configuration
    # number_of_rooms = configuration.number_of_rooms
    get_room_by_id = configuration.get_room_by_id

    rooms = configuration._rooms
    sections = configuration._sections

    # for section in sections:
    #     if section.room_id is not None:
    #         print(section)

    sections_dict_list = []
    for section in sections:
        room_id = section.room_id
        room_name = get_room_by_id(room_id).name
        dict = Section.section_to_dict(section)
        dict["Room"] = room_name
        sections_dict_list.append(dict)

    json_string = json.dumps(sections_dict_list, indent=4)

    # Write the JSON string to the file
    file_path = "sections.json"

    # Write the JSON string to the file
    with open(file_path, 'w') as json_file:
        json_file.write(json_string)

    print("JSON data saved to", file_path)

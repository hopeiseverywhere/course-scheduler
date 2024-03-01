import json
# from model.Configuration import Configuration
from model.Schedule import Schedule
from model.Section import Section


def get_result(solution: Schedule):
    configuration = solution.configuration
    get_room_by_id = configuration.get_room_by_id
    sections = configuration._sections


    sections_dict_list = []
    for section in sections:
        section.set_actual_time()
        room_id = section.room_id
        room_name = get_room_by_id(room_id).name
        dict = Section.section_to_dict(section)
        dict["Room"] = room_name
        sections_dict_list.append(dict)

    json_string = json.dumps(sections_dict_list, indent=4)
    return json_string

    # # Write the JSON string to the file
    # file_path = "sections.json"
    #
    # # Write the JSON string to the file
    # with open(file_path, 'w') as json_file:
    #     json_file.write(json_string)
    #
    # print("JSON data saved to", file_path)


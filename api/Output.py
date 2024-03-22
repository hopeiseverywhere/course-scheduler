import json
# from model.Configuration import Configuration
from model.Schedule import Schedule
from model.Section import Section
import os

main_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(main_dir, "..", "io_data", "output.json")


def get_result(solution: Schedule):
    """
    convert GA result to json and or local file
    """
    solution.print_criteria()
    solution.update_final_criteria()
    configuration = solution.configuration
    get_room_by_id = configuration.get_room_by_id
    sections = configuration.sections

    sections_dict_list = []
    for section in sections:
        section.set_actual_time()
        room_id = section.room_id
        room_name = get_room_by_id(room_id).name
        section_dict = Section.section_to_dict(section)
        section_dict["Room"] = room_name
        sections_dict_list.append(section_dict)

    # sort the list by section id
    sections_dict_list = sorted(sections_dict_list,
                                key=lambda x: x["Section Id"])
    # print(sections_dict_list)

    json_string = json.dumps(sections_dict_list, indent=4)

    # Write the JSON string to the file
    # file_path = "../io_data/output.json"
    with open(file_path, 'w') as json_file:
        json_file.write(json_string)
    print("JSON data saved to", file_path)
    print("Final Fitness: ",solution.fitness)
    return json_string

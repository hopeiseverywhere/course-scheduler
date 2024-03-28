import json
import os
# from model.Configuration import Configuration
from model.Schedule import Schedule
from model.Section import Section
from model.Criteria import Criteria
from io_data.json_csv_converter import convert_json_to_csv

json_file_name = "output_json.json"
main_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(main_dir, "..", "io_data", json_file_name)
Criteria = Criteria


def get_result(solution: Schedule):
    """
    convert GA result to json and or local file
    """

    configuration = solution.configuration
    get_room_by_id = configuration.get_room_by_id
    final_criteria = solution.final_criteria

    # Sort the list of sections so criteria satisfaction
    # for each course can be easily checked
    sections = sorted(configuration.sections, key=lambda x: x.section_id)
    criteria_size = Criteria.criteria_size

    sections_dict_list = []
    for section in sections:
        # Set whether all criteria satisfied for each course
        sublist = final_criteria[section.section_id]
        if False in sublist:
            section.criteria_met = False
        else:
            section.criteria_met = True
        section.set_actual_time()
        room_id = section.room_id
        room_name = get_room_by_id(room_id).name
        section_dict = Section.section_to_dict(section)
        section_dict["Room"] = room_name
        sections_dict_list.append(section_dict)

    json_string = json.dumps(sections_dict_list, indent=4)

    # Write the JSON string to the file
    with open(file_path, 'w') as json_file:
        json_file.write(json_string)
    # save a csv version as well
    convert_json_to_csv(json_file_name)

    print("JSON data saved to", file_path)
    print("Final Fitness: ", solution.fitness)
    print("Fitness = {} / {}".format(solution.score, solution.criteria_length))
    return json_string

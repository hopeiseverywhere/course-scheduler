import json
# from model.Configuration import Configuration
from model.Schedule import Schedule
from model.Section import Section
from model.Criteria import Criteria
import os

main_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(main_dir, "..", "io_data", "output.json")
Criteria = Criteria

def get_result(solution: Schedule):
    """
    convert GA result to json and or local file
    """
    
    configuration = solution.configuration
    get_room_by_id = configuration.get_room_by_id
    final_criteria = solution.final_criteria

    # Sort the list of sections so criteria satisfaction for each course can be easily checked
    sections = sorted(configuration.sections, key=lambda x: x.section_id)
    criteria_size = Criteria.criteria_size

    # Set whether all criteria satisfied for each course
    # for i in range(0, solution.criteria_length, criteria_size):
    #     sections[i // criteria_size].set_criteria_met(all(solution.criteria[i:i + criteria_size]))
    # for sec_id in range(0, configuration.number_of_sections):
    #     for ci in range(0, solution.criteria_size):
            


    sections_dict_list = []
    for section in sections:
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

    # sort the list by section id
    # sections_dict_list = sorted(sections_dict_list,
    #                             key=lambda x: x["Section Id"])

    json_string = json.dumps(sections_dict_list, indent=4)

    # Write the JSON string to the file
    # file_path = "../io_data/output.json"
    with open(file_path, 'w') as json_file:
        json_file.write(json_string)
    print("JSON data saved to", file_path)
    print("Final Fitness: ",solution.fitness)
    print("Fitness = {} / {}".format(solution.score, solution.criteria_length))
    return json_string

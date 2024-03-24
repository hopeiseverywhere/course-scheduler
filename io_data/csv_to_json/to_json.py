import csv
import os
import json


def day_to_index(day):
    days_mapping = {
        'Monday': 0,
        'Tuesday': 1,
        'Wednesday': 2,
        'Thursday': 3,
        'Friday': 4,
        'Saturday': 5,
        'Sunday': 6
    }
    return days_mapping.get(day, None)


def convert_csv_to_json(csv_file):
    # Directory of the current script
    script_dir = os.path.dirname(os.path.realpath(__file__))
    # Full path to the CSV file
    file_path = os.path.join(script_dir, csv_file)

    data = []

    with open(file_path, 'r', newline='') as csvfile:
        csvreader = csv.DictReader(csvfile)
        # Print column names
        print("Column names:", csvreader.fieldnames)
        for row in csvreader:
            # course
            course_number = row['Course #']
            # student size
            cap_value = row['Cap']
            if cap_value and cap_value.strip().isdigit():
                students = int(cap_value)
            else:
                students = 0  # Assign a default value or handle it accordingly
            # lab
            course_name = row['Course Title']
            if 'Recitation' in course_name:
                is_lab = True
            else:
                is_lab = False
            # day
            pref_day = [row['Day']]
            pref_day = pref_day[0].split(', ')
            pref_day = list(map(day_to_index, pref_day))
            # print(pref_day)
            # time
            pref_time = [row['Time'].lower()]
            pref_time = pref_time[0].split(', ')

            # duration
            if is_lab:
                duration = 100
            else:
                duration = 200

            section = {
                "section": {
                    "course": course_number,  # Corrected column name
                    "professor": row['Prof'],
                    "pref_time": pref_time,
                    "pref_day": pref_day,
                    "is_lab": is_lab,  # Assuming all courses are not labs
                    "duration": duration,  # Assuming fixed duration
                    "students": students
                }
            }
            data.append(section)

    return data


def main():

    csv_file_name = 'input.csv'
    json_data = convert_csv_to_json(csv_file_name)
    # print(json.dumps(json_data, indent=4))

    script_dir = os.path.dirname(os.path.realpath(__file__))
    output_json_file = os.path.join(script_dir, 'all_sections.json')
    with open(output_json_file, 'w') as json_file:
        json.dump(json_data, json_file, indent=4)

    print(f"JSON data has been saved to {output_json_file}")


if __name__ == "__main__":
    main()

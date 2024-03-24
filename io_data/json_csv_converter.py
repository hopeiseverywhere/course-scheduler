import csv
import os
import json
from datetime import datetime


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


def index_to_day(idx):
    day_mapping = {
        0: 'Monday',
        1: 'Tuesday',
        2: 'Wednesday',
        3: 'Thursday',
        4: 'Friday',
        5: 'Saturday',
        6: 'Sunday'
    }
    return day_mapping.get(idx, None)

def convert_time_to_ampm(time_str):
    # Parse time string to datetime object
    time_obj = datetime.strptime(time_str, "%H:%M")
    # Format datetime object to AM/PM format
    return time_obj.strftime("%I:%M %p")


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

    # Saving the JSON data
    output_json_file = os.path.join(script_dir, 'input_json.json')
    with open(output_json_file, 'w') as json_file:
        json.dump(data, json_file, indent=4)

    print(f"JSON data has been saved to {output_json_file}")


def convert_json_to_csv(json_file):
    # Directory of the current script
    script_dir = os.path.dirname(os.path.realpath(__file__))
    # Full path to the JSON file
    json_file_path = os.path.join(script_dir, json_file)

    with open(json_file_path, 'r') as json_file:
        data = json.load(json_file)

    # Define the header fields for the CSV
    fieldnames = ['Section Id', 'Course', 'Prof', 'Start Day',
                  'Start Time', 'End Time', 'Room', 'Criteria Satisfied']

    # Directory for the output CSV file
    csv_file_path = os.path.join(script_dir, 'output_csv.csv')

    with open(csv_file_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for item in data:
            day = index_to_day(item.get('Start Day', ''))
            # Convert start and end time to AM/PM format
            start_time = convert_time_to_ampm(item.get('Start Time', ''))
            end_time = convert_time_to_ampm(item.get('End Time', ''))

            writer.writerow({
                'Section Id': item.get('Section Id', ''),
                'Course': item.get('Course', ''),
                'Prof': item.get('Prof', ''),
                'Start Day': day,
                'Start Time': start_time,
                'End Time': end_time,
                'Room': item.get('Room', ''),
                'Criteria Satisfied': item.get('Criteria Satisfied', '')
            })

    print(f"CSV data has been saved to {csv_file_path}")


def main():

    # csv_file_name = 'input.csv'
    # convert_csv_to_json(csv_file_name)
    json_file_name = 'output_json.json'
    convert_json_to_csv(json_file_name)


if __name__ == "__main__":
    main()

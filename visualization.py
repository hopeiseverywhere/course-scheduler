import json
import pandas as pd
import webbrowser
import os

# Read data from JSON file
with open("sections.json", "r") as file:
    data = json.load(file)

# Convert the JSON data into a DataFrame
df = pd.DataFrame(data)

# Define the days of the week and time slots
days_of_week = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday",
                4: "Friday"}
time_slots = [
    "09:50 - 10:10", "10:10 - 10:30", "10:30 - 10:50", "10:50 - 11:10",
    "11:10 - 11:30", "11:30 - 11:50", "11:50 - 12:10", "12:10 - 12:30",
    "12:30 - 12:50", "12:50 - 13:10", "13:10 - 13:30", "13:30 - 13:50",
    "13:50 - 14:10", "14:10 - 14:30", "14:30 - 14:50", "14:50 - 15:10",
    "15:10 - 15:30", "15:30 - 15:50", "15:50 - 16:10", "16:10 - 16:30",
    "16:30 - 16:50", "16:50 - 17:10", "17:10 - 17:30", "17:30 - 17:50",
    "17:50 - 18:10", "18:10 - 18:30", "18:30 - 18:50", "18:50 - 19:10",
    "19:10 - 19:30", "19:30 - 19:50", "19:50 - 20:10", "20:10 - 20:30",
    "20:30 - 20:50", "20:50 - 21:10", "21:10 - 21:30", "21:30 - 21:50"
]

# Group the DataFrame by Room
grouped_by_room = df.groupby("Room")

# Initialize an empty string to store HTML representations of timetables
html_output = ""

# Iterate over each classroom
for room, room_data in grouped_by_room:
    # Initialize an empty timetable DataFrame
    timetable = pd.DataFrame(index=time_slots,
                             columns=[days_of_week[day] for day in
                                      sorted(days_of_week.keys())])

    # Fill in the timetable DataFrame with course information for the current classroom
    for _, row in room_data.iterrows():
        day = days_of_week[row["Start Day"]]
        relative_start = row["Relative Start"]
        dur = row["Dur"]
        end_slot_index = relative_start + dur - 1
        start_time = time_slots[relative_start]
        end_time = time_slots[end_slot_index]
        course_info = f"{row['Course']}<br>{row['Prof']}"

        # Calculate the span of time slots for the course
        start_slot_index = time_slots.index(start_time)
        end_slot_index = time_slots.index(end_time)

        # Add course information to each time slot it spans
        for i in range(start_slot_index, end_slot_index + 1):
            timetable.loc[time_slots[i], day] = course_info

    timetable.fillna('', inplace=True)
    # Convert the timetable DataFrame to HTML and append to the html_output string
    html_output += f"<h2>Timetable for Classroom: {room}</h2>\n"
    html_output += '<style>table { table-layout: fixed; width: 100%; }</style>'  # Set fixed layout
    html_output += '<style>td { width: 100px; height: 50px; }</style>'  # Set width and height of each cell
    html_output += timetable.to_html(
        escape=False) + "<br><br>\n"  # Disabling HTML escaping

# Write the combined HTML output to a file
html_file_path = "timetable.html"
with open(html_file_path, "w") as html_file:
    html_file.write(html_output)

# Open the generated HTML file in a web browser
webbrowser.open("file://" + os.path.realpath(html_file_path))

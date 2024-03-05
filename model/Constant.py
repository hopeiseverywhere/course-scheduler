# segment time by an hour
DAYS_NUM = 5
# DAY_HOURS = 12
# DAY_START_HOUR = 9


# relative time
# morning = 9 - 12
# afternoon = 12 - 17
# evening = 17 - 21
time_ranges2 = {
    "morning": [0, 4],
    "afternoon": [4, 7],
    "evening": [7, 12]
}

# Segment time by 30 minutes
# actual day is from 9:30 to 21:50
# 12 hours, 20 minutes -> 740 minutes

# preferably from 10 to 21:50
# 11 hours, 50 minutes -> 710 minutes, odd number so
# lets go from 9:50 to 21:50
# 12 hours, 0 minute -> 720 minutes
# slice segment into 20 minutes -> 36 slots

# main course: 3 hour and 20 minutes or 200 minutes
# -> duration: 10 slots
# lab: 90 minutes -> make it 100 minutes
# -> duration 5 slots

# segment time by 20 minutes
TIME_SEGMENT = 20
# so there are 60 slots per day
DAY_SLOTS = 36

# for instance, day start at 9:50
DAY_START_HOUR = 9
DAY_START_MINUTES = 50

MINUTES_TO_HOUR = 1 / 60
HOUR_TO_MINUTES = 60

# morning = 9:50 - 12:30 -> duration 2:40 -> 160 minutes -> 8 slots
# afternoon = 12:30 - 17:30 -> duration 5 hour -> 15 slots
# evening = 17:30 - 21:50 -> duration 4 hour 20 minutes -> 13 slots
time_ranges = {
    "morning": [0, 8],
    "afternoon": [8, 23],
    "evening": [23, 36]
}

# Dictionary to relate labs to their main classes. Usage will check if course is a lab before accessing dictionary,
# which is why key = lab, val = main course
lab_main_courses = {
    "5003": "5001",
    "5005": "5004",
    "5009": "5008",
    "5011": "5010"
}

# Courses which are paired together because they are typically taken together. Usage is ensuring at least one of each
# does not conflict with the other
concurrent_courses = {
    "5001": "5002", "5002": "5001",
    "5004": "5008", "5008": "5004",
    "5010": "5800", "5800": "5010"
}

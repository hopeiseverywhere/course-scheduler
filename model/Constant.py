# segment time by an hour
DAYS_NUM = 5
DAY_HOURS = 12
DAY_START_HOUR = 9


# relative time
# morning = 9 - 12
# afternoon = 12 - 17
# evening = 17 - 21
time_ranges = {
    "morning": [0, 4],
    "afternoon": [4, 7],
    "evening": [7, 12]
}

# Segment time by 20 minutes
# actual day is from 9:30 to 21:50
# 12 hours, 20 minutes -> 740 minutes

# preferably from 10 to 21:50
# 11 hours, 50 minutes -> 710 minutes, odd number so
# lets go from 9:50 to 21:50
# 12 hours, 0 minute -> 720 minutes
# slice segment into 20 minutes -> 36 slots

# main course: 3 hour and 20 minutes or 200 minutes -> 10 slots
# lab: 90 minutes -> make it 100 minutes -> 5 slots

DAY_SLOTS = 60
# morning = 9:50 - 12:30 -> duration 2:40
# afternoon = 12:30 - 17:30 -> duration 5
# evening = 17:30 - 21:50 -> duration 4
time_ranges2 = {
    "morning": [0, 8],
    "afternoon": [8, 23],
    "evening": [23, 35]
}

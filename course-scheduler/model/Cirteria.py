# Reads configuration file and stores parsed objects
from model import Constant
from model.Room import Room
from model.Section import Section


class Criteria:
    # 4 criteria for calculating fitness
    # weights = [0, 0.5, 0.5, 0, 0]
    weights = [0, 0.25, 0, 0.25]

    # 0. check for room overlapping of classes
    @staticmethod
    def is_room_overlapped(slots, reservation, dur):
        reservation_index = hash(reservation)
        sections = slots[reservation_index: reservation_index + dur]
        return any(True for slot in sections if len(slot) > 1)

    # 1. check seat enough
    @staticmethod
    def is_seat_enough(r: Room, section: Section):
        return r.Number_Of_Seats >= section.Number_Of_Seats

    # 2. professor overlap
    @staticmethod
    def is_prof_overlapped(slots, section, number_of_rooms, time_id):
        po = False

        dur = section.Duration
        for i in range(number_of_rooms, 0, -1):
            # for each hour of class
            for j in range(time_id, time_id + dur):
                cl = slots[j]
                for section1 in cl:
                    if section != section1:
                        # professor overlaps?
                        if not po and section.professor_overlaps(section1):
                            po = True

                        # overlapping? no need to check more
                        if po:
                            return po

            time_id += Constant.DAY_HOURS
        return po

    # 3. professor satisfied
    @staticmethod
    def is_prof_satisfied(section: Section, start_time: int, end_time: int):
        return (start_time >= section.Preference_range[0] and
                end_time <= section.Preference_range[1])

# Reads configuration file and stores parsed objects
from model import Constant
from model.Room import Room
from model.Section import Section


class Criteria:
    # 4 criteria for calculating fitness
    # weights = [0, 0.5, 0.5, 0, 0]
    weights = [0.25, 0.25, 0.5, 0.5, 0.5]

    # 0. check for room overlapping of classes
    @staticmethod
    def is_room_overlapped(slots, reservation, dur):
        reservation_index = hash(reservation)
        sections = slots[reservation_index: reservation_index + dur]
        return any(True for slot in sections if len(slot) > 1)

    # 1. check seat enough
    @staticmethod
    def is_seat_enough(r: Room, section: Section):
        return r.number_of_seats >= section.number_of_students

    # 2. professor overlap
    @staticmethod
    def is_prof_overlapped(slots, section, number_of_rooms, time_id):
        po = False

        dur = section.duration
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

            time_id += Constant.DAY_SLOTS
        return po

    # 3. professor satisfied
    @staticmethod
    def is_prof_satisfied(section: Section, start_time: int, end_time: int):
        return (start_time >= section.pref_time_range[0] and
                end_time <= section.pref_time_range[1])

    # 4. Lab timings satisfied
    @staticmethod
    def is_lab_satisfied(lab_section: Section, section_table):
        # Return true if not a lab - these checks won't be necessary for main courses
        if not lab_section.is_lab:
            return True

        # Get the corresponding main course for the lab
        main_course_num = Constant.lab_main_courses[lab_section.course_name]
        # Check that corresponding course (number + professor pair) starts at roughly same time on different day
        for compare_section in section_table:
            # Only check times if correct section found
            if compare_section.course_name == main_course_num and lab_section.prof_name == compare_section.prof_name:
                lab_start_time = int(lab_section.start_time[:2])
                main_course_start_time = int(compare_section.start_time[:2])
                difference_start_times = lab_start_time - main_course_start_time
                max_diff = 1
                return lab_section.day != compare_section.day and -max_diff <= difference_start_times <= max_diff

        # If all sections checked for a lab and no corresponding main course found, return false
        return False

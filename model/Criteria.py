# Reads configuration file and stores parsed objects
from typing import List, Dict
from model import Constant
from model.Room import Room
from model.Section import Section
from model.Reservation import Reservation


class Criteria:
    # 4 criteria for calculating fitness
    # weights = [0, 0.5, 0.5, 0, 0]
    weights = [0.0, 0.25, 0.5, 0.5, 0.25, 0.5]
    criteria_size = len(weights)

    # 0. check for room overlapping of classes
    @staticmethod
    def is_room_overlapped(slots: List[List[Section]], reservation: Reservation,
        dur: int):
        """
        Check if there is any room overlap for the given reservation
        """
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
        for _i in range(number_of_rooms, 0, -1):
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
    # @staticmethod
    # def is_lab_satisfied(lab_section: Section, section_table):
    #     # Return True if not a lab -
    #     # these checks won't be necessary for main courses
    #     if not lab_section.is_lab:
    #         return True
    #
    #     # Get the corresponding main course for the lab
    #     main_course_num = Constant.lab_main_courses[lab_section.course_name]
    #     # Check that corresponding course
    #     # (number + professor pair) starts at roughly same time on different day
    #     for compare_section in section_table:
    #         # Only check times if correct section found
    #         if (compare_section.course_name == main_course_num
    #             and lab_section.prof_name == compare_section.prof_name):
    #             lab_start_time = int(lab_section.start_time[:2])
    #             main_course_start_time = int(compare_section.start_time[:2])
    #             difference_start_times = lab_start_time - main_course_start_time
    #             max_diff = 2
    #
    #             # Return True if on different day and within
    #             # max difference of starting time, False otherwise
    #             return (lab_section.day != compare_section.day
    #                     and -max_diff <= difference_start_times <= max_diff)
    #
    #     # If all sections checked for a lab
    #     # and no corresponding main course found, return False
    #     return False

    @staticmethod
    def is_lab_satisfied(lab_section: Section, main_section: Section) -> bool:
        """Return true if lab section's timing is satisfied,
        false other wise

        Args:
            lab_section (Section): lab section
            main_section (Section): lab section's corresponding main section

        Returns:
            bool: 
        """
        # Return True if not a lab -
        # these checks won't be necessary for main courses
        if not lab_section.is_lab or main_section is None:
            return True
        lab_start_time = lab_section.relative_start
        main_course_start_time = main_section.relative_start
        difference_start_times = abs(lab_start_time - main_course_start_time)
        max_diff = int(Constant.HOUR_TO_MINUTES / Constant.TIME_SEGMENT)
        day_diff = abs(lab_section.day - main_section.day)

        # Return True if on different day and within
        # max difference of starting time, False otherwise
        return (day_diff > 1
                and difference_start_times <= max_diff)

    # 5. Concurrent courses allow for one non-overlapped option
    # @staticmethod
    # def concurrent_course_option_available1(section, section_table):
    #     # If course is not a concurrent course, return True
    #     if not Constant.concurrent_courses.__contains__(section.course_name):
    #         return True
    #
    #     # Partner course number from table
    #     partner_course = Constant.concurrent_courses.get(section.course_name)
    #
    #     # Compare with each course and count
    #     # the number of its partner course that do not conflict
    #     non_conflicting_partners = 0
    #     for compare_section in section_table:
    #         if compare_section.course_name == partner_course:
    #             # If partner course and on different day, cannot be overlapped
    #             if section.day != compare_section.day:
    #                 non_conflicting_partners += 1
    #                 continue
    #
    #             # If partner course and on same day,
    #             # check if overlapped. Do not increment count if overlapped,
    #             # otherwise increment count
    #             curr_start = section.relative_start
    #             curr_end = compare_section.relative_start
    #             comp_start = section.relative_start
    #             comp_end = compare_section.relative_start
    #             if (comp_start <= curr_start <= comp_end
    #                 or comp_start <= curr_end <= comp_end):
    #                 continue
    #             else:
    #                 non_conflicting_partners += 1
    #                 continue
    #
    #         # If at least one partner course is not overlapped, return True.
    #         # Else return False
    #         return non_conflicting_partners >= 1

    @staticmethod
    def is_conflict(section: Section,
        conflicts_dict: Dict[Section, List[Section]]) -> bool:
        """Check if current section has a concurrent conflict section

        Args:
            section (Section): current section
            conflicts_dict (Dict[Section, List[Section]]): a dictionary in configuration that stores all concurrent conflict sections data

        Returns:
            bool: if yes, return true, otherwise return false
        """
        # If the course don't have a conflict course, return false
        if section not in conflicts_dict.keys():
            return False

        conflict_sections = conflicts_dict[section]
        # Compare with each course and count
        # the number of its partner course that do not conflict
        non_conflicting_partners = 0
        for compare_section in conflict_sections:
            # If partner course and on different day, cannot be overlapped
            if section.day != compare_section.day:
                non_conflicting_partners += 1
                continue
            else:
                # If partner course and on same day,
                # check if overlapped. Do not increment count if overlapped,
                # otherwise increment count
                if Criteria.is_time_overlap(section, compare_section):
                    continue
                else:
                    non_conflicting_partners += 1
                    continue

        # If all partner sections are non conflict, return false
        # Else return true
        return non_conflicting_partners < len(conflict_sections)

    @staticmethod
    def is_time_overlap(section1: Section, section2: Section) -> bool:
        """
        If two sections time overlaps, return true, else return false
        """
        if section1.relative_start is None or section2.relative_start is None:
            return False
        curr_start = section1.relative_start
        curr_end = section1.relative_start
        comp_start = section2.relative_start
        comp_end = section2.relative_start
        return (comp_start <= curr_start <= comp_end or
                comp_start <= curr_end <= comp_end)

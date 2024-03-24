# Reads configuration file and stores parsed objects
from typing import List, Dict
from model import Constant
from model.Room import Room
from model.Section import Section
from model.Reservation import Reservation
from model.Configuration import Configuration


class Criteria:
    # 7 criteria for calculating fitness
    # 0 - 1, 0 is more important, 1 is not important
    weights = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    criteria_size = len(weights)

    # 0. check for room overlapping of classes
    @staticmethod
    def is_room_overlapped(room_slot: Dict[int, Dict[int, List[bool | int]]], sec_id: int, dur: int,  day: int, relative_time: int, room_id: int):
        """
        Check if there is any room overlap for the given reservation
        """
        sublist = []
        for i in range(relative_time, relative_time + dur):
            sublist.append(room_slot[room_id][day][i])
        
        if all(el is False for el in sublist):
            # Condition 1: All elements are False -> room is not occupied
            return False

        count_false = 0
        count_id = 0
        for el in sublist:
            if el is False:
                count_false += 1
            elif el == sec_id:
                count_id += 1
            elif el is not False and el != sec_id:
                # print(sec_id ,"is conflict with id", el)
                # Condition 2: If any element is not equal to sec_id and not false, room is occupied
                return True
                
        # Condition 3: If false count + section count == length of sublist -> room is not occupied
        if count_false + count_id == len(sublist):
            return False

        # Condition 2: If any element is not equal to sec_id, room is occupied
        return any(el != sec_id for el in sublist)
        

    # 1. check seat enough
    @staticmethod
    def is_seat_enough(r: Room, section: Section):
        return r.number_of_seats >= section.number_of_students

    # 2. professor overlap
    @staticmethod
    def is_prof_overlapped1(slots, section, number_of_rooms, time_id):
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
    
    @staticmethod
    def is_prof_overlapped(section: Section, sections: List[Section]):
        for section1 in sections:
            if section1.section_id == section.section_id:
                continue
            if section1.professor_overlaps(section):
                return True
        return False

    # 3. professor satisfied
    @staticmethod
    def is_prof_satisfied(pref_time_range: List[int], start_time: int,
                          end_time: int):
        # loose prof satisfied range a little bit
        max_diff = 3
        return (start_time >= pref_time_range[0] - max_diff and
                end_time <= pref_time_range[1] + max_diff)

    # 4. Lab timings satisfied
    # @staticmethod
    # def is_lab_satisfied(lab_section: Section, main_section: Section) -> bool:
    #     """Return true if lab section's timing is satisfied,
    #     false otherwise

    #     Args:
    #         lab_section (Section): lab section
    #         main_section (Section): lab section's corresponding main section

    #     Returns:
    #         bool:
    #     """
    #     # Return True if not a lab -
    #     # these checks won't be necessary for main courses
    #     if not lab_section.is_lab or main_section is None:
    #         return True
    #     lab_start_time = lab_section.relative_start
    #     main_course_start_time = main_section.relative_start
    #     difference_start_times = abs(lab_start_time - main_course_start_time)
    #     max_diff = int(Constant.HOUR_TO_MINUTES / Constant.TIME_SEGMENT)
    #     day_diff = abs(lab_section.day - main_section.day)

    #     # Return True if on different day and within
    #     # max difference of starting time, False otherwise
    #     # return (day_diff > 1
    #     #         and difference_start_times <= max_diff)

    #     # now only check day diff > 1
    #     return day_diff > 1

    @staticmethod
    def is_lab_satisfied(sec: Section, config: Configuration) -> bool:
        """Return true if lab section's timing is satisfied,
        false otherwise

        """
        # Return True if not a lab nor not linked to a lab

        if not config.is_section_linked_to_lab(sec):
            return True

        linked = config.get_linked_section(sec)
        # max_diff = int(Constant.HOUR_TO_MINUTES / Constant.TIME_SEGMENT)
        day_diff = abs(sec.day - linked.day)

        # Return True if on different day and within
        # max difference of starting time, False otherwise
        return (day_diff > 1)

    # 5. Concurrent courses allow for one non-overlapped option

    @staticmethod
    def is_conflict(section: Section,
                    conflicts_dict: Dict[Section, List[Section]]) -> bool:
        """Check if current section has a concurrent conflict section

        Args:
            section (Section): current section
            conflicts_dict (Dict[Section, List[Section]]): a dictionary in
            configuration that stores all concurrent conflict sections data

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

    # 6. is day satisfied
    @staticmethod
    def is_day_satisfied(pref_days: List[int], day: int) -> bool:
        if day in pref_days:
            return True
        return False

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

    @staticmethod
    def is_time_and_day_overlap(section1: Section, section2: Section) -> bool:
        return Criteria.is_time_overlap(section1, section2) and section1.day == section2.day

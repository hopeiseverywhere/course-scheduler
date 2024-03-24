from model import Constant
from model.Reservation import Reservation
from collections import defaultdict


class HtmlOutput:
    ROOM_COLUMN_NUMBER = Constant.DAYS_NUM + 1
    ROOM_ROW_NUMBER = Constant.DAY_SLOTS + 1
    COLOR1 = "#319378"
    COLOR2 = "#CE0000"
    CRITERIAS = ('RO', 'SE', 'PO', 'TI', 'LB', 'CC', 'DA')
    OK_DESCR = ("Current room has no overlapping",
                "Current room has enough seats",
                "Professor not overlapped",
                "Professor time preferences met",
                "Lab timing requirements met",
                "Concurrent course requirements met",
                "Professor day preferences met")
    FAIL_DESCR = ("Current room has overlapping",
                  "Current room has not enough seats",
                  "Professor is overlapped",
                  "Professors time preference not satisfied",
                  "Lab does not have proper timing",
                  "Course cannot be taken with a concurrent required course",
                  "Professor day is not met")
    # PERIODS = (
    #     "", "9 - 10", "10 - 11", "11 - 12", "12 - 13", "13 - 14", "14 - 15", "15 - 16", "16 - 17", "17 - 18", "18 - 19",
    #     "19 - 20", "20 - 21")
    # segment by 20 minutes
    PERIODS = (
        "", "9:50 - 10:10", "10:10 - 10:30", "10:30 - 10:50", "10:50 - 11:10",
        "11:10 - 11:30", "11:30 - 11:50",
        "11:50 - 12:10", "12:10 - 12:30", "12:30 - 12:50", "12:50 - 13:10",
        "13:10 - 13:30", "13:30 - 13:50",
        "13:50 - 14:10", "14:10 - 14:30", "14:30 - 14:50", "14:50 - 15:10",
        "15:10 - 15:30", "15:30 - 15:50",
        "15:50 - 16:10", "16:10 - 16:30", "16:30 - 16:50", "16:50 - 17:10",
        "17:10 - 17:30", "17:30 - 17:50",
        "17:50 - 18:10", "18:10 - 18:30", "18:30 - 18:50", "18:50 - 19:10",
        "19:10 - 19:30", "19:30 - 19:50",
        "19:50 - 20:10", "20:10 - 20:30", "20:30 - 20:50", "20:50 - 21:10",
        "21:10 - 21:30", "21:30 - 21:50"
    )
    

    WEEK_DAYS = ("MON", "TUE", "WED", "THU", "FRI", "SAT")

    @staticmethod
    def getCourseClass(cc, criteria, section_id):
        COLOR1 = HtmlOutput.COLOR1
        COLOR2 = HtmlOutput.COLOR2
        CRITERIAS = HtmlOutput.CRITERIAS
        length_CRITERIAS = len(CRITERIAS)

        sb = [cc.course_num, "<br />", "ID " +
              str(cc.section_id), "<br />", cc.prof_name, "<br />"]
        if cc.is_lab:
            sb.append("Is lab<br />")
        print("here: ",section_id, criteria[section_id])
        for i in range(length_CRITERIAS):
            sb.append("<span style='color:")
            
            if criteria[section_id][i] is True:
                sb.append(COLOR1)
                sb.append("' title='")
                sb.append(HtmlOutput.OK_DESCR[i])
            elif criteria[section_id][i] is False:
                sb.append(COLOR2)
                sb.append("' title='")
                sb.append(HtmlOutput.FAIL_DESCR[i])
            sb.append("'> ")
            sb.append(CRITERIAS[i])
            sb.append(" </span>")

        # print(sb)
        return sb

    @staticmethod
    def generateTimeTable(solution, slot_table):
        ci = 0

        time_table = defaultdict(list)
        items = solution.sections_table.items
        ROOM_COLUMN_NUMBER = HtmlOutput.ROOM_COLUMN_NUMBER
        getCourseClass = HtmlOutput.getCourseClass

        
        for section, reservation_index in items():
            # reservation = Reservation.parse(reservation_index)

            # coordinate of time-space slot
            dayId = section.day + 1
            periodId = section.relative_start + 1
            roomId = section.room_id
            dur = section.duration

            key = (periodId, roomId)
            if key in slot_table:
                room_duration = slot_table[key]
            else:
                room_duration = ROOM_COLUMN_NUMBER * [0]
                slot_table[key] = room_duration
            room_duration[dayId] = dur

            for m in range(1, dur):
                next_key = (periodId + m, roomId)
                if next_key not in slot_table:
                    slot_table[next_key] = ROOM_COLUMN_NUMBER * [0]
                if slot_table[next_key][dayId] < 1:
                    slot_table[next_key][dayId] = -1

            if key in time_table:
                room_schedule = time_table[key]
            else:
                room_schedule = ROOM_COLUMN_NUMBER * [None]
                time_table[key] = room_schedule

            room_schedule[dayId] = "".join(
                getCourseClass(section, solution.final_criteria, section.section_id))
            

        return time_table

    @staticmethod
    def getHtmlCell(content, rowspan):
        if rowspan == 0:
            return "<td></td>"

        if content is None:
            return ""

        sb = []
        if rowspan > 1:
            sb.append(
                "<td style='border: .1em solid black; padding: .25em' rowspan='")
            sb.append(rowspan)
            sb.append("'>")
        else:
            sb.append("<td style='border: .1em solid black; padding: .25em'>")

        sb.append(content)
        sb.append("</td>")
        return "".join(str(v) for v in sb)

    @staticmethod
    def getResult(solution):
        configuration = solution.configuration
        nr = configuration.number_of_rooms
        getRoomById = configuration.get_room_by_id

        slot_table = defaultdict(list)
        time_table = HtmlOutput.generateTimeTable(
            solution, slot_table)  # Tuple[0] = time, Tuple[1] = roomId
        if not slot_table or not time_table:
            return ""

        sb = []
        for roomId in range(nr):
            room = getRoomById(roomId)
            for periodId in range(HtmlOutput.ROOM_ROW_NUMBER):
                if periodId == 0:
                    sb.append("<div id='room_")
                    sb.append(room.name)
                    sb.append("' style='padding: 0.5em'>\n")
                    sb.append(
                        "<table style='border-collapse: collapse; width: 95%'>\n")
                    sb.append(HtmlOutput.getTableHeader(room))
                else:
                    key = (periodId, roomId)
                    # print(key)
                    room_duration = slot_table[key] if key in slot_table.keys(
                    ) else None
                    room_schedule = time_table[key] if key in time_table.keys(
                    ) else None
                    sb.append("<tr>")
                    for dayId in range(HtmlOutput.ROOM_COLUMN_NUMBER):
                        if dayId == 0:
                            sb.append(
                                "<th style='border: .1em solid black; padding: .25em' scope='row' colspan='2'>")
                            sb.append(HtmlOutput.PERIODS[periodId])
                            sb.append("</th>\n")
                            continue

                        if room_schedule is None and room_duration is None:
                            continue

                        content = room_schedule[dayId] if room_schedule is not None else None
                        sb.append(HtmlOutput.getHtmlCell(
                            content, room_duration[dayId]))
                    sb.append("</tr>\n")

                if periodId == HtmlOutput.ROOM_ROW_NUMBER - 1:
                    sb.append("</table>\n</div>\n")

        return "".join(str(v) for v in sb)

    @staticmethod
    def getTableHeader(room):
        sb = ["<tr><th style='border: .1em solid black' scope='col' colspan='2'>Room: ",
              room.name, "</th>\n"]
        for weekDay in HtmlOutput.WEEK_DAYS:
            sb.append(
                "<th style='border: .1em solid black; padding: .25em; width: 15%' scope='col' rowspan='2'>")
            sb.append(weekDay)
            sb.append("</th>\n")
        sb.append("</tr>\n")
        sb.append("<tr>\n")
        sb.append("<th style='border: .1em solid black; padding: .25em'>Lab: ")

        sb.append("<th style='border: .1em solid black; padding: .25em'>Seats: ")
        sb.append(room.number_of_seats)
        sb.append("</th>\n")
        sb.append("</tr>\n")
        return "".join(str(v) for v in sb)

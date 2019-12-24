from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import *
from .serializers import *
from django.db.models import Q
from .testprolog import PrologMT
# from pyswip import Prolog



# Create your views here.
class Holidays(APIView):
    
    # This one shows the days to be compensated and a endpoint to be call the prolog predicate
    # Get Holidays
    def get(self, request, format=None):
        return Response(CalendarHolidaySerializer(CalendarHoliday.objects.all(), many=True).data)

    # Post a New Holiday
    def post(self, request, format=None):
        ser = CalendarHolidaySerializer(data=request.data)
        if(ser.is_valid()):
            ser.save()
            return Response(ser.data)
        return Response()

class Compensations(APIView):

    def post(self, request, format=None):
        holiday = HolidayCompensationSerializer(data=request.data)

        if(holiday.is_valid()):
            # Get Holiday date 
            holiday_details = CalendarHoliday.objects.get(pk=holiday.data['id'])
            holiday_date = holiday_details.date
            holiday_day  = holiday_details.day.pk

            meetings_on_holiday = list(CourseMeeting.objects.filter(Q(course_start_date__lte=holiday_date) & Q(course_end_date__gte=holiday_date) & Q(day=holiday_day), Q(midterm_start_date__gt=holiday_date) | Q(midterm_end_date__lt=holiday_date)))
            
            ################################## Compensations ##########################
            compensations = []
            count = 0
            for meeting in meetings_on_holiday:
                
                holidays_set = set()
                # Get staff member holidays
                staff_holidays = list(meeting.staff_member.holidays.all())
                for staff_holiday in staff_holidays:
                    holidays_set.add(staff_holiday.day - 1)

                tutorials = []
                if(meeting.slot_type == CourseMeeting.LECTURE):
                    # In case of lecture get all it's corresponding tutorials
                    tutorials = list(TutorialGroup.objects.filter(lecture_group=meeting.lecture_group.pk).only())

                    # Replace Tutorial object with its primary key & get tutorial group holidays
                    i = 0
                    while(i < len(tutorials)):

                        # Get Tutorial Group Holidays
                        tutorial_holidays = list(tutorials[i].holidays.all())
                        for tutorial_holiday in tutorial_holidays:
                            holidays_set.add(tutorial_holiday.day - 1)

                        tutorials[i] = tutorials[i].pk
                        i += 1
                else:
                    # Get Tutorial Group Holidays
                    tutorial_holidays = list(meeting.tutorial.holidays.all())
                    for tutorial_holiday in tutorial_holidays:
                        holidays_set.add(tutorial_holiday.day - 1)
                
                    tutorials.append(meeting.tutorial_group.pk)
                
                # Tut = 0, LargeHall = 1, SmallHall = 2, Lab = 3
                room_type = 0
                if(meeting.room.room_type == Room.LARGE_HALL):
                    room_type = 1
                elif(meeting.room.room_type == Room.SMALL_HALL):
                    room_type = 2
                elif(meeting.room.room_type == Room.LAB):
                    room_type = 3

                # (StaffID , Semester , Course , Tutorials (List) , RoomType (0, 3) , DaysOff (List of daysoff), RoomSlot (HashFunction))
                staff_member_group_tuple = (meeting.staff_member.pk, meeting.lecture_group.semester, meeting.course.pk, tutorials, room_type, list(holidays_set), count)# Last attribute Should be a Var
                compensations.append(staff_member_group_tuple)
                count += 1
                # days_off.append( (staff_member_group_tuple, list(holidays_set)))
            
            print(compensations)
            print()
            # print(days_off)
            # print()

            ################################## FreeRooms ##########################
            free_rooms = []
            all_rooms = list(Room.objects.all())
            all_meetings = CourseMeeting.objects.filter(~Q(day=holiday_day)) 

            for room in all_rooms:

                days_in_week = 6
                slots_in_day = 5
                isFree = [[True for i in range(slots_in_day)] for j in range(days_in_week)] 

                occupied_rooms = list(all_meetings.filter(Q(room=room.pk)))
                for occupied_room in occupied_rooms:
                    isFree[occupied_room.day.pk - 1][occupied_room.slot - 1] = False

                i = 0
                while(i < days_in_week):
                    j = 0
                    while(j < slots_in_day):
                        if(isFree[i][j] and i + 1 != holiday_day):
                            free_rooms.append( calculate_room_slot_hash(room.pk, room.room_type, i, j) )
                        j += 1
                    i += 1

            print(free_rooms)
            print()

            ################################## Preferences ##################################
            preferrable = []
            not_preferable = []
            preferences = list(Preferences.objects.all())
            for preference in preferences:
                if(preference.is_preffered):
                    preferrable.append( calculate_staff_slot_hash(preference.staff_member.pk, preference.day.pk - 1, preference.slot - 1) )
                else:
                    not_preferable.append( calculate_staff_slot_hash(preference.staff_member.pk, preference.day.pk - 1, preference.slot - 1) )

            print(preferrable)
            print()
            print(not_preferable)
            print()

            ################################## OriginalSlots ##########################
            original_slots = []
            meetings_in_week = list(CourseMeeting.objects.filter(~Q(day=holiday_day)))
            for meeting in meetings_in_week:
                
                holidays_set = set()
                # Get staff member holidays
                staff_holidays = list(meeting.staff_member.holidays.all())
                for staff_holiday in staff_holidays:
                    holidays_set.add(staff_holiday.day - 1)

                tutorials = []
                if(meeting.slot_type == CourseMeeting.LECTURE):
                    # In case of lecture get all it's corresponding tutorials
                    tutorials = list(TutorialGroup.objects.filter(lecture_group=meeting.lecture_group.pk).only())
                    # Replace Tutorial object with its primary key
                    i = 0
                    while(i < len(tutorials)):

                        # Get Tutorial Group Holidays
                        tutorial_holidays = list(tutorials[i].holidays.all())
                        for tutorial_holiday in tutorial_holidays:
                            holidays_set.add(tutorial_holiday.day - 1)

                        tutorials[i] = tutorials[i].pk
                        i += 1
                else:
                    # Get Tutorial Group Holidays
                    tutorial_holidays = list(meeting.tutorial.holidays.all())
                    for tutorial_holiday in tutorial_holidays:
                        holidays_set.add(tutorial_holiday.day - 1)

                    tutorials.append(meeting.tutorial_group.pk)

                # Tut = 0, LargeHall = 1, SmallHall = 2, Lab = 3
                room_type = 0
                if(meeting.room.room_type == Room.LARGE_HALL):
                    room_type = 1
                elif(meeting.room.room_type == Room.SMALL_HALL):
                    room_type = 2
                elif(meeting.room.room_type == Room.LAB):
                    room_type = 3
                
                # (StaffID , Semester , Course , Tutorials (List) , RoomType (0, 3) , DaysOff (List of daysoff), RoomSlot (HashFunction))
                original_slots_tuple = (meeting.staff_member.pk, meeting.lecture_group.semester, meeting.course.pk, tutorials, room_type, list(holidays_set), calculate_room_slot_hash(meeting.room.pk, meeting.room.room_type, meeting.day.pk - 1, meeting.slot - 1))
                original_slots.append(original_slots_tuple)

            print(original_slots)
            print()

            
            ################################## PrologQuery ##########################
            print(stringify_compensations_original(compensations, original_slots))
            print()
            print(stringify_free_rooms(free_rooms))
            print()
            print(stringify_preferences(preferrable))
            print()
            print(stringify_preferences(not_preferable))
            print()

            final_query = "solve(" + stringify_compensations_original(compensations, original_slots) + "," + stringify_free_rooms(free_rooms) + "," + stringify_preferences(preferrable) + "," + stringify_preferences(not_preferable) + ")"
            # prologtest()
            prolog = PrologMT()
            # print(2333344)
            # prolog.assertz("father(michael,john)")
            # print(list(prolog.query("father(michael,X)")))

            print("hahahahaha")
            print()
            # prolog.consult("/Users/omaremad/Desktop/CompensationSystemProject/Compensation-System/compensation_backend/compensationapp/PopQuiz.pl")
            # print(list(prolog.query("which_house(A, B, C, D)")))
            prolog.consult("/Users/omaremad/Desktop/CompensationSystemProject/Compensation-System/compensation_backend/compensationapp/ProjectCLPFD-3.pl")
            print(list(prolog.query(final_query)))
            print()
            
            return Response(CourseMeetingSerializer(meetings_on_holiday, many=True).data)


######################################### HELPERS #################################
def calculate_room_slot_hash(room_id, room_type_string, day, slot):
    # Tut = 0, LargeHall = 1, SmallHall = 2, Lab = 3
    room_type = 0
    if(room_type_string == Room.LARGE_HALL):
        room_type = 1
    elif(room_type_string == Room.SMALL_HALL):
        room_type = 2
    elif(room_type_string == Room.LAB):
        room_type = 3

    return (room_id * 4 * 6 * 5) + (room_type * 6 * 5) + (day * 5) + slot

def calculate_staff_slot_hash(staff_id, day, slot):
    return (staff_id * 6 * 5) + (day * 5) + slot

def stringify_free_rooms(free_rooms):
    query_string = "["

    j = 0
    for room in free_rooms:
        query_string += str(room)

        if(j + 1 < len(free_rooms)):
            query_string += ","
        j += 1
    
    query_string += "]"
    return query_string

def stringify_preferences(preferences):
    query_string = "["

    j = 0
    for preference in preferences:
        query_string += str(preference)

        if(j + 1 < len(preferences)):
            query_string += ","
        j += 1
    
    query_string += "]"
    return query_string

def stringify_compensations_original(compensations, originals):
    query_string = "["

    length = len(compensations) + len(originals)

    j = 0
    for compensation in compensations:
        # Staff, Semester, Course
        query_string += "(" + str(compensation[0]) + "," + str(compensation[1]) + "," + str(compensation[2]) + ","
        # Tutorials
        query_string += "[" 
        i = 0
        while(i < len(compensation[3])):
            query_string += str(compensation[3][i])
            if(i + 1 < len(compensation[3])):
                query_string += ","
            else:
                query_string += "],"
            i += 1

        # Room Type
        query_string += str(compensation[4]) + ","

        # DaysOff
        query_string += "[" 
        i = 0
        while(i < len(compensation[5])):
            query_string += str(compensation[5][i])
            if(i + 1 < len(compensation[5])):
                query_string += ","
            else:
                query_string += "],"
            i += 1

        # RoomSlot (HashFunction) But here will be variable
        query_string += "C" + str(compensation[6]) + ")"

        if(j + 1 < length):
            query_string += ","
        j += 1

    for original in originals:
        # Staff, Semester, Course
        query_string += "(" + str(original[0]) + "," + str(original[1]) + "," + str(original[2]) + ","
        # Tutorials
        query_string += "[" 
        i = 0
        while(i < len(original[3])):
            query_string += str(original[3][i])
            if(i + 1 < len(original[3])):
                query_string += ","
            else:
                query_string += "],"
            i += 1

        # Room Type
        query_string += str(original[4]) + ","

        # DaysOff
        query_string += "[" 
        i = 0
        while(i < len(original[5])):
            query_string += str(original[5][i])
            if(i + 1 < len(original[5])):
                query_string += ","
            else:
                query_string += "],"
            i += 1

        # RoomSlot (HashFunction) But here will be variable
        query_string += str(original[6]) + ")"

        if(j + 1 < length):
            query_string += ","
        j += 1

    query_string += "]"

    return query_string



        

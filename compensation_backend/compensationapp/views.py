from django.shortcuts import render
# from rest_framework.views import APIView
# from rest_framework.response import Response
from .models import *
from .serializers import *
from django.db.models import Q
from .testprolog import PrologMT
from datetime import datetime, timedelta
# from rest_framework.permissions import IsAuthenticated  # <-- Here

# Frontend Forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django import forms

class Logout(View):

    def get(self, request):
        logout(request)
        return HttpResponseRedirect('/login')


class Login(View):
    template = 'login.html'

    def get(self, request):
        print(request.user.is_authenticated)
        form = AuthenticationForm()
        return render(request, self.template, {'form': form})


    def post(self, request):
        # print(request.user.is_authenticated)

        form = AuthenticationForm(request.POST)
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if(user.is_superuser):
                return HttpResponseRedirect('/gucadmin/holidays')
            else:
                return HttpResponseRedirect('/gucstaff/compensations/')
        else:
            return render(request, self.template, {'form': form})
        return render(request, self.template)

# Create your views here.
class Holidays(LoginRequiredMixin, View):
    template = "index.html"
    login_url = '/login/'

    # This one shows the days to be compensated and a endpoint to be call the prolog predicate
    # Get Holidays
    def get(self, request, format=None):
        print(request.user.is_authenticated)
        holidays = CalendarHoliday.objects.all()
        return render(request, self.template, {'holidays': holidays})
        # return Response(CalendarHolidaySerializer(CalendarHoliday.objects.all(), many=True).data)

    # # Post a New Holiday
    # def post(self, request, format=None):
    #     ser = CalendarHolidaySerializer(data=request.data)
    #     if(ser.is_valid()):
    #         ser.save()
    #         return Response(ser.data)
    #     return Response()

class PreferencesForm(forms.Form):
    FIRST = 1
    SECOND = 2
    THIRD = 3
    FOURTH = 4
    FIFTH = 5
    SLOT_CHOICES = (
        (FIRST, '1ST'),
        (SECOND, '2ND'),
        (THIRD, '3RD'),
        (FOURTH, '4TH'),
        (FIFTH, '5TH'),
    )

    SATURDAY = 1
    SUNDAY = 2
    MONDAY = 3
    TUESDAY = 4
    WEDNESDAY = 5
    THURSDAY = 6
    DAY_CHOICES = (
        (SATURDAY, 'Saturday'),
        (SUNDAY, 'Sunday'),
        (MONDAY, 'Monday'),
        (TUESDAY, 'Tuesday'),
        (WEDNESDAY, 'Wednesday'),
        (THURSDAY, 'Thursday'),
    )

    slot = forms.CharField(label='Select Slot?', widget=forms.Select(choices=SLOT_CHOICES))
    day = forms.CharField(label='Select Day?', widget=forms.Select(choices=DAY_CHOICES))
    isPreffered = forms.BooleanField(required=False)

class StaffPreferences(View):
    login_url = '/login/'
    template = "preferences.html"
    def get(self, request):
        staff = StaffMember.objects.get(user=request.user)
        return render(request, self.template, {'preferences': Preferences.objects.filter(staff_member=staff), 'preferences_form':PreferencesForm()})

    def post(self, request):
        day = request.POST['day']
        slot = request.POST['slot']
        isPreffered = request.POST.get('isPreffered', False)
        if(isPreffered == 'on'):
            isPreffered = True
        staff = StaffMember.objects.get(user=request.user)
        week_day = WeekDay.objects.get(day=day)
        isAdded = Preferences.objects.filter(Q(staff_member=staff) & Q(day=week_day) & Q(slot=slot))
        if(len(isAdded) > 0):
            return HttpResponseRedirect('/gucstaff/preferences/')
        else:
            pref = Preferences(staff_member=staff, slot=slot, day=week_day, is_preffered=isPreffered)
            pref.save()
            return HttpResponseRedirect('/gucstaff/preferences/')

class StaffCompensations(View):
    login_url = '/login/'
    template = "compensations_staff.html"
    def get(self, request):
        staff = StaffMember.objects.get(user=request.user)
        return render(request, self.template, {'compensations': Compensation.objects.filter(course_meeting__staff_member=staff)})

class CompensationsView(View):
    # permission_classes = (IsAuthenticated,)             # <-- And here
    login_url = '/login/'
    template = "compensations_admin.html"

    def get(self, request):
        return render(request, self.template, {'compensations': Compensation.objects.all()})

    def post(self, request, format=None):
        holiday_id = request.POST["holiday_id"]

        # if(holiday.is_valid()):
            # Get Holiday date 
        holiday_details = CalendarHoliday.objects.get(pk=holiday_id)
        holiday_date = holiday_details.date
        holiday_day  = holiday_details.day.pk

        isCompensated = Compensation.objects.filter(holiday=holiday_details)
        if(len(isCompensated) > 0):
            return render(request, self.template, {'compensations': Compensation.objects.all()})

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
                for lecture in list(meeting.lecture_group.all()):
                    for tut in list(TutorialGroup.objects.filter(lecture_group=lecture.pk).only()):
                        tutorials.append(tut)

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
            staff_member_group_tuple = (meeting.staff_member.pk, 5, meeting.course.pk, tutorials, room_type, list(holidays_set), count, meeting)# Last attribute Should be a Var
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
                # print(meeting.lecture_group)
                # In case of lecture get all it's corresponding tutorials
                for lecture in list(meeting.lecture_group.all()):
                    for tut in list(TutorialGroup.objects.filter(lecture_group=lecture.pk).only()):
                        tutorials.append(tut)
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
            original_slots_tuple = (meeting.staff_member.pk, 5, meeting.course.pk, tutorials, room_type, list(holidays_set), calculate_room_slot_hash(meeting.room.pk, meeting.room.room_type, meeting.day.pk - 1, meeting.slot - 1))
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
        prolog = PrologMT()
        print("hahahahaha")
        print()
        # prolog.consult("/Users/omaremad/Desktop/CompensationSystemProject/Compensation-System/compensation_backend/compensationapp/PopQuiz.pl")
        # print(list(prolog.query("which_house(A, B, C, D)")))
        prolog.consult("/Users/omaremad/Desktop/CompensationSystemProject/Compensation-System/compensation_backend/compensationapp/compensation_scheduler.pl")
        results = list(prolog.query(final_query, maxresult=1))
        i = 0
        print(results)
        while i < len(compensations):
            new_slot_tuple = room_slot_dehash(results[0]["C" + str(i)])
            
            print(new_slot_tuple)
            print(StaffMember.objects.get(pk=compensations[i][0]).user.username)
            print(Course.objects.get(pk=compensations[i][2]).name)
            print(list(compensations[i][7].lecture_group.all()))
            
            new_date = None
            if(new_slot_tuple[2] > compensations[i][7].day.pk):
                new_date = holiday_date + timedelta(days=new_slot_tuple[2] - compensations[i][7].day.pk)
            else:
                new_date = holiday_date - timedelta(days=compensations[i][7].day.pk - new_slot_tuple[2])
            print(new_date)

            new_room = Room.objects.get(pk=new_slot_tuple[1])
            print(new_room)
            new_day = WeekDay.objects.get(pk=new_slot_tuple[2])
            new_meeting = Compensation(course_meeting=compensations[i][7], date=new_date, day=new_day, slot=new_slot_tuple[3], room=new_room, holiday=holiday_details)
            new_meeting.save()
            # Create Compensation Here
            i += 1
        
        # return Response(CourseMeetingSerializer(meetings_on_holiday, many=True).data)
        return HttpResponseRedirect('/gucadmin/holidays')


######################################### HELPERS #################################
def room_slot_dehash(room_slot_hash):
    slot = room_slot_hash % 5
    day = (room_slot_hash // 5) % 6
    room_type = (room_slot_hash // 30) % 4
    room_id = (room_slot_hash // (30 * 4)) % 50
    return (room_id, room_type, day + 1, slot + 1)

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



# calculate_preferable([] , Preferable , 0).
# calculate_preferable([(StaffID , _ , _ , _ , _ ,_,RoomSlot) | T] , Preferable, Score):-
# 	Slot #= RoomSlot mod 30 , 
# 	Hash #= StaffID * 200 + Slot , 
# 	calculate_preferable(T , Preferable , Score1),
# 	(( element(_,Preferable , Hash), Score #= Score1 + 1 ) ;  \+ element(_,Preferable , Hash)).
    
# calculate_days_off([(_ , _ , _ , _ , _ ,DaysOFF,RoomSlot) | T] , Score):- 
# 		Day #= (RoomSlot // 5)  mod 6, 
# 		calculate_days_off(T , Score1) , 
# 		((element(_ ,DaysOFF , Day) , Score #= Score1 + 4) ; \+ element(_ ,DaysOFF , Day)). 

# solve([(9,5,8,[4,5,6,7,8],1,[0,3,4],C0),(3,5,2,[9,10,11,12,13,14],1,[1,3,4],150),(3,5,2,[4,5,6,7,8],1,[1,3,4],151),(4,5,3,[15,16],1,[1,2,3,4],272),(5,5,4,[4,5,6,7,8],1,[0,3,4],395),(6,5,5,[4,5,6,7,8],1,[0,3,4],396),(7,5,7,[9,10,11,12,13,14,15,16],1,[3,4],276),(6,5,5,[9,10,11,12,13,14,15,16],1,[0,3,4],397),(8,5,6,[4,5,6,7,8],1,[0,2,3,4],398),(5,5,4,[9,10,11,12,13,14,15,16],1,[0,3,4],535),(8,5,6,[9,10,11,12,13,14,15,16],1,[0,2,3,4],536),(7,5,7,[4,5,6,7,8],1,[3,4],537)],[152,153,154,155,156,157,158,159,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,270,271,273,274,275,277,278,279,285,286,287,288,289,290,291,292,293,294,295,296,297,298,299,390,391,392,393,394,399,405,406,407,408,409,410,411,412,413,414,415,416,417,418,419,510,511,512,513,514,515,516,517,518,519,525,526,527,528,529,530,531,532,533,534,538,539,630,631,632,633,634,635,636,637,638,639,645,646,647,648,649,650,651,652,653,654,655,656,657,658,659],[82],[],S)
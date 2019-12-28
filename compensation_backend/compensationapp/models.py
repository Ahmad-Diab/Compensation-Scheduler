from django.db import models
from django.conf import settings



# Staff_Members (ID, Name)
# Staff_Members_Holidays (ID, StaffMemberID, Day) will be many to many field with in staff member
# Courses (ID, Name)
# Rooms (ID, RoomName, RoomType)
# Lecture_Groups (ID, Name)
# Tutorial_Groups (ID, TutorialGroupName, LectureGroupID) 
# Tutorial_Group_Holidays (ID, TutorialGroupID, LectureGroupID, Day) will be many to many field with tutorial groups
# Calendar_Holidays (ID, HolidayName, Date, Day)
# Course_Meetings (ID, CourseID, StaffMemberID, Day, Slot, LectureGroupID, TutorialGroupID, RoomID, SlotType, CourseStartDate, CourseEndDate, MidTermStartDate, MidtermEndDate, IsFirstYear)
# Compensations (ID, MeetingID, Date, Day, Slot, RoomID, CalendarHolidayID)


# Create your models here.


class WeekDay(models.Model):

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
    day = models.PositiveIntegerField(choices=DAY_CHOICES, primary_key=True)

    def __str__(self):
        return self.DAY_CHOICES[self.day - 1][1]

class StaffMember(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    holidays = models.ManyToManyField(WeekDay)
    
    def __str__(self):
        return self.user.username

class Preferences(models.Model):

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

    staff_member = models.ForeignKey(StaffMember, on_delete=models.CASCADE)
    is_preffered = models.BooleanField()
    day = models.ForeignKey(WeekDay, on_delete=models.CASCADE)
    slot = models.PositiveIntegerField(choices=SLOT_CHOICES)

    def __str__(self):
        return self.staff_member.__str__()

class Course(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Room(models.Model):

    ROOM = 'Room'
    LAB = 'Lab'
    SMALL_HALL = 'Small Hall'
    LARGE_HALL = 'Large Hall'
    ROOM_CHOICES = (
        (ROOM, 'Room'),
        (LAB, 'Lab'),
        (SMALL_HALL, 'Small Hall'),
        (LARGE_HALL, 'Large Hall'),
    )

    name = models.CharField(max_length=200)
    room_type = models.CharField(max_length=20, choices=ROOM_CHOICES)

    def __str__(self):
        return self.name

class LectureGroup(models.Model):
    lecture_group_name = models.CharField(max_length=200)
    semester = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.lecture_group_name

class TutorialGroup(models.Model):
    tutorial_group_name = models.CharField(max_length=200)
    lecture_group = models.ForeignKey(LectureGroup, on_delete=models.CASCADE)
    holidays = models.ManyToManyField(WeekDay)

    def __str__(self):
        return self.tutorial_group_name

class CalendarHoliday(models.Model):
    holiday_name = models.CharField(max_length=200)
    date = models.DateField()
    day = models.ForeignKey(WeekDay, on_delete=models.CASCADE)

    def __str__(self):
        return self.holiday_name

class CourseMeeting(models.Model):

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

    TUTORIAL = 1
    LAB = 2
    LECTURE = 3
    SLOT_TYPE_CHOICES = (
        (TUTORIAL, 'Tutorial'),
        (LAB, 'Lab'),
        (LECTURE, 'Lecture'),
    )

    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    staff_member = models.ForeignKey(StaffMember, on_delete=models.CASCADE)
    day = models.ForeignKey(WeekDay, on_delete=models.CASCADE)
    slot = models.PositiveIntegerField(choices=SLOT_CHOICES)
    lecture_group = models.ManyToManyField(LectureGroup)
    tutorial_group = models.ForeignKey(TutorialGroup, on_delete=models.CASCADE, null=True, blank=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    slot_type = models.PositiveIntegerField(choices=SLOT_TYPE_CHOICES)
    course_start_date = models.DateField()
    course_end_date = models.DateField()
    midterm_start_date = models.DateField()
    midterm_end_date = models.DateField()
    is_first_year = models.BooleanField()

    def __str__(self):
        return str(self.course) + " / " + str(self.staff_member.__str__())

class Compensation(models.Model):
    
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
    course_meeting = models.ForeignKey(CourseMeeting, on_delete=models.CASCADE)
    date = models.DateField()
    day = models.ForeignKey(WeekDay, on_delete=models.CASCADE)
    slot = models.PositiveIntegerField(choices=SLOT_CHOICES)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    holiday = models.ForeignKey(CalendarHoliday, on_delete=models.CASCADE)
    

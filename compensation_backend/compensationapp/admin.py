from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(WeekDay)
admin.site.register(StaffMember)
admin.site.register(Preferences)
admin.site.register(Course)
admin.site.register(Room)
admin.site.register(LectureGroup)
admin.site.register(TutorialGroup)
admin.site.register(CalendarHoliday)
admin.site.register(CourseMeeting)
admin.site.register(Compensation)
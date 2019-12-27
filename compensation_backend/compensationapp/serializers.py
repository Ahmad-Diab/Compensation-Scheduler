# from rest_framework import serializers
# from .models import *

# class WeekDaySerializer(serializers.Serializer):
#     day = serializers.CharField()

# class CalendarHolidaySerializer(serializers.ModelSerializer):
#     # day = serializers.StringRelatedField()
#     # id = serializers.IntegerField(read_only=True)
#     # holiday_name = serializers.CharField()
#     # date = serializers.DateField()
#     class Meta:
#         model = CalendarHoliday
#         fields = ['id', 'holiday_name', 'date', 'day']

# class HolidayCompensationSerializer(serializers.Serializer):
#     id = serializers.IntegerField()
    
# class CourseMeetingSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CourseMeeting
#         fields = [
#             'course', 
#             'staff_member',
#             'day',
#             'slot',
#             'lecture_group',
#             'tutorial_group',
#             'room',
#             'slot_type',
#             'course_start_date',
#             'course_end_date',
#             'midterm_start_date',
#             'midterm_end_date',
#             'is_first_year'
#         ]
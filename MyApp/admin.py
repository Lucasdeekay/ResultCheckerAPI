from django.contrib import admin
from .models import Student, Course, Result, Notification, Grade


# Register Student Model
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('matric_no', 'last_name', 'first_name', 'programme', 'level')
    search_fields = ('matric_no', 'last_name', 'first_name')


# Register Course Model
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_code', 'course_name')
    search_fields = ('course_code', 'course_name')


# Register Result Model
@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'semester', 'session', 'score')
    search_fields = (
        'student__matric_no', 'student__last_name', 'course__course_code', 'course__course_name', 'semester', 'session')

    def student_matric_no(self, obj):
        return obj.student.matric_no

    def student_name(self, obj):
        return f"{obj.student.last_name} {obj.student.first_name}"


# Register Notification Model
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'content', 'date')
    search_fields = ('title', 'content')


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('student', 'semester', 'session', 'gpa',)
    search_fields = ('student__matric_no', 'semester', 'session',)

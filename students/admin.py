from django.contrib import admin
from .models import StudentEnrollment, StudentLearningProgress
# Register your models here.

#admin.site.register(StudentEnrollment)

class StudentLearningProgressInline(admin.StackedInline):
    model = StudentLearningProgress

@admin.register(StudentEnrollment)
class StudentEnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'date']
    inlines = [StudentLearningProgressInline]

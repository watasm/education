from django.contrib import admin
from .models import Subject, Course, Module, Quiz, Question, QuestionChoices, StudentQuestionAnswer
from students.models import StudentEnrollment

admin.site.index_template = 'memcache_status/admin_index.html'

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug']
    prepopulated_fields = {'slug': ('title', )}

class ModuleInline(admin.StackedInline):
    model = Module

class StudentEnrollmentInline(admin.StackedInline):
    model = StudentEnrollment

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'created']
    list_filter = ['created', 'subject']
    search_fields = ['title', 'overview']
    prepopulated_fields = {'slug': ('title', )}
    inlines = [ModuleInline, StudentEnrollmentInline]


class QuestionChoicesInline(admin.StackedInline):
    model = QuestionChoices

class StudentQuestionAnswerInline(admin.StackedInline):
    model = StudentQuestionAnswer

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    inlines = [QuestionChoicesInline, StudentQuestionAnswerInline]

admin.site.register(Quiz)

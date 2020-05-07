from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.views.generic.base import TemplateResponseMixin, View
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CourseEnrollForm
from courses.models import Course, Content, Module, Question, StudentQuestionAnswer
from .models import StudentEnrollment, StudentLearningProgress
from courses.forms import QuestionAnswerForm

from django.contrib.auth.mixins import UserPassesTestMixin

class NotInstructorMixin(UserPassesTestMixin):
    def test_func(self):
        return not self.request.user.groups.filter(name='Instructors').exists()


class StudentEnrollCourseView(LoginRequiredMixin, NotInstructorMixin, FormView):
    course = None
    form_class = CourseEnrollForm

    def form_valid(self, form):
        self.course = form.cleaned_data['course']
        StudentEnrollment.objects.create(course=self.course, student=self.request.user)
        return super(StudentEnrollCourseView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('student_course_detail', args=[self.course.id])

class StudentCourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'students/course/list.html'

    def get_queryset(self):
        qs = super(StudentCourseListView, self).get_queryset()
        return qs.filter(students__student=self.request.user)


class StudentCourseDetailView(NotInstructorMixin, DetailView):
    model = Course
    object = None
    module = None
    content = None
    template_name = 'students/course/detail.html'

    def get_queryset(self):
        qs = super(StudentCourseDetailView, self).get_queryset()
        return qs.filter(students__student=self.request.user)

    def dispatch(self, request, pk, module_id=None, content_id=None):
        # get course
        self.object = self.get_object()

        #get module
        if module_id:
            self.module = self.object.modules.get(id=module_id)
        else:
            self.module = self.object.modules.first()

        # get content
        if content_id:
            self.content = self.module.contents.get(id=content_id)
        else:
            self.content = None
        return super(StudentCourseDetailView, self).dispatch(request, pk, module_id, content_id)


    def get(self, request, pk, module_id=None, content_id=None):
        # question_answer_form = None
        # is_right = None
        if self.content:
            enrollment = get_object_or_404(StudentEnrollment, course=self.object, student=self.request.user)
            if not StudentLearningProgress.objects.filter(enrollment=enrollment, content=self.content).exists():
                StudentLearningProgress.objects.create(enrollment=enrollment, content=self.content)

            # if isinstance(self.content.item, Question):
            #     question_answer_form = QuestionAnswerForm(data=request.GET, question=self.content.item)
            #
            #     #if student already answered
            #     if StudentQuestionAnswer.objects.filter(student=self.request.user, question=self.content.item).exists():
            #         answer = StudentQuestionAnswer.objects.get(student=self.request.user, question=self.content.item)
            #         is_right = answer.is_right

        return render(request, self.template_name, {'object': self.object, 'module': self.module, 'content': self.content})


    def post(self, request, pk, module_id, content_id):
        return render(request, self.template_name, {'object': self.object, 'module': self.module, 'content': self.content})
        #return self.render_to_response(self.template_name, context)


    #def get_context_data(self, **kwargs):
        #context = super(StudentCourseDetailView, self).get_context_data(**kwargs)

        #get course object
        #course = self.get_object()

        # if 'module_id' in self.kwargs:
        #     # get current module
        #     context['module'] = course.modules.get(id=self.kwargs['module_id'])
        # else:
        #     #get first module
        #     context['module'] = course.modules.first()

        # if 'content_id' in self.kwargs:
        #     # get current content
        #     context['content'] = context['module'].contents.get(id=self.kwargs['content_id'])
        #     if isinstance(context['content'].item, Question):
        #         context['question_answer_form'] = QuestionAnswerForm(question=context['content'].item)
        #
        #     enrollment = get_object_or_404(StudentEnrollment, course=course, student=self.request.user)
        #     if not StudentLearningProgress.objects.filter(enrollment=enrollment, content=context['content']).exists():
        #         StudentLearningProgress.objects.create(enrollment=enrollment, content=context['content'])
        #
        # return context


# class StudentCourseDetailView(DetailView):
#     model = Course
#     template_name = 'students/course/detail.html'
#
#     def get_queryset(self):
#         qs = super(StudentCourseDetailView, self).get_queryset()
#         return qs.filter(students__student=self.request.user)
#
#     def get_context_data(self, **kwargs):
#         context = super(StudentCourseDetailView, self).get_context_data(**kwargs)
#
#         #get course object
#         course = self.get_object()
#
#         if 'module_id' in self.kwargs:
#             # get current module
#             context['module'] = course.modules.get(id=self.kwargs['module_id'])
#         else:
#             #get first module
#             context['module'] = course.modules.first()
#
#         if 'content_id' in self.kwargs:
#             # get current content
#             context['content'] = context['module'].contents.get(id=self.kwargs['content_id'])
#             if isinstance(context['content'].item, Question):
#                 context['question_answer_form'] = QuestionAnswerForm(question=context['content'].item)
#
#             enrollment = get_object_or_404(StudentEnrollment, course=course, student=self.request.user)
#             if not StudentLearningProgress.objects.filter(enrollment=enrollment, content=context['content']).exists():
#                 StudentLearningProgress.objects.create(enrollment=enrollment, content=context['content'])
#
#         return context

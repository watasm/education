from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import Course, Module, Content, Subject, Quiz, Question, QuestionChoices, StudentQuestionAnswer
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic.base import TemplateResponseMixin, View
from .forms import ModuleFormSet, QuestionChoicesFormSet, QuestionForm
from django.forms.models import modelform_factory
from django.apps import apps
from braces.views import CsrfExemptMixin, JsonRequestResponseMixin
from django.db.models import Count
from django.views.generic.detail import DetailView
from students.forms import CourseEnrollForm
from django.core.cache import cache
from students.models import StudentEnrollment, StudentLearningProgress
from django.http import JsonResponse
from django.contrib import messages
from django.views.generic.edit import FormView
from django.views.decorators.http import require_http_methods
from django.utils import timezone


class OwnerMixin(object):
    def get_queryset(self):
        qs = super(OwnerMixin, self).get_queryset()
        return qs.filter(owner=self.request.user)

class OwnerEditMixin(object):
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super(OwnerEditMixin, self).form_valid(form)

class OwnerCourseMixin(OwnerMixin, LoginRequiredMixin):
    model = Course
    fields = ['subject', 'title', 'slug', 'overview']
    success_url = reverse_lazy('manage_course_list')

class OwnerCourseEditMixin(OwnerCourseMixin, OwnerEditMixin):
    fields = ['subject', 'title', 'slug', 'overview']
    success_url = reverse_lazy('manage_course_list')
    template_name = 'courses/manage/course/form.html'

class ManageCourseListView(OwnerCourseMixin, ListView):
    template_name = 'courses/manage/course/list.html'

class CourseCreateView(PermissionRequiredMixin, OwnerCourseEditMixin, CreateView):
    permission_required = 'courses.add_course'

class CourseUpdateView(PermissionRequiredMixin, OwnerCourseEditMixin, UpdateView):
    permission_required = 'courses.change_course'

class CourseDeleteView(PermissionRequiredMixin, OwnerCourseMixin, DeleteView):
    template_name = 'courses/manage/course/delete.html'
    success_url = reverse_lazy('manage_course_list')
    permission_required = 'courses.delete_course'


class CourseModuleUpdateView(OwnerCourseEditMixin, TemplateResponseMixin, View):
    template_name = 'courses/manage/module/formset.html'
    course = None

    def get_formset(self, data=None):
        return ModuleFormSet(instance=self.course, data=data)

    def dispatch(self, request, pk):
        self.course = get_object_or_404(Course, id=pk, owner=request.user)
        return super(CourseModuleUpdateView, self).dispatch(request, pk)

    def get(self, request, *args, **kwargs):
        formset = self.get_formset()
        return self.render_to_response({'course': self.course, 'formset': formset})

    def post(self, request, *args, **kwargs):
        formset = self.get_formset(data=request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('manage_course_list')

        return self.render_to_response({'course': self.course, 'formset': formset})

class ContentCreateUpdateView(OwnerCourseEditMixin, CreateView):
    module = None
    model = None
    object = None
    template_name = 'courses/manage/content/newform.html'
    #success_url = 'success/'

    def get_model(self, model_name):
        if model_name in ['text', 'video', 'image', 'file', 'quiz']:
            return apps.get_model(app_label='courses', model_name=model_name)
        return None

    def get_form(self, model, *args, **kwargs):
        Form = modelform_factory(model, exclude=['owner', 'order', 'created', 'updated'])
        return Form(*args, **kwargs)

    def dispatch(self, request, module_id, model_name, id=None):
        self.module = get_object_or_404(Module, id=module_id, course__owner=request.user)
        self.model = self.get_model(model_name)
        if id:
            self.object = get_object_or_404(self.model, id=id, owner=request.user)

        return super(ContentCreateUpdateView, self).dispatch(request, module_id, model_name, id)

    def get(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.object)
        return self.render_to_response(self.get_context_data(form=form, object=self.object, module_id=self.module.id))

    def post(self, request, module_id, model_name, id):
        form = self.get_form(self.model, instance=self.object, data=self.request.POST)
        if form.is_valid():
            self.object = form.save(commit=False)
            self.object.owner = self.request.user
            self.object.save()

            if not id:
                # new content
                Content.objects.create(module=self.module, item=self.object)

        return self.render_to_response({'form': form, 'object': self.object, 'module_id': module_id})

class QuizQuestionCreateUpdateView(LoginRequiredMixin, UpdateView):
    model = Question
    form_class = QuestionForm
    module = None
    quiz = None
    object = None
    template_name = 'courses/manage/content/quiz/questions.html'

    def dispatch(self, request, module_id, quiz_id, id=None):
        self.module = get_object_or_404(Module, id=module_id, course__owner=request.user)
        self.quiz = get_object_or_404(Quiz, id=quiz_id, owner=request.user)
        if id:
            self.object = get_object_or_404(Question, id=id, quiz=self.quiz)

        return super(QuizQuestionCreateUpdateView, self).dispatch(request, module_id, quiz_id, id)

    def get(self, request, module_id, quiz_id, id=None):
        question_choices_formset = QuestionChoicesFormSet(instance=self.object)
        return self.render_to_response(self.get_context_data(object=self.object, question_choices_formset=question_choices_formset))

    def post(self, request, module_id, quiz_id, id=None):
        form = self.get_form(self.form_class)
        question_choices_formset = QuestionChoicesFormSet(instance=self.object, data=self.request.POST)

        if form.is_valid():
            if question_choices_formset.is_valid():
                return self.form_valid(form, question_choices_formset)
            else:
                return self.form_valid(form, None)
        else:
            return self.form_invalid(form, question_choices_formset)

        return self.render_to_response(self.get_context_data(object=self.object, question_choices_formset=question_choices_formset))

    def form_valid(self, form, question_choices_formset):
        self.object = form.save(commit=False)
        self.object.quiz = self.quiz
        self.object.save()

        if question_choices_formset:
            question_choices_formset.instance = self.object
            question_choices_formset.save()

        question_choices_formset = QuestionChoicesFormSet(instance=self.object)
        return self.render_to_response(self.get_context_data(object= self.object, question_choices_formset=question_choices_formset))

    def form_invalid(self, form, question_choices_formset):
        return self.render_to_response(self.get_context_data(question_choices_formset=question_choices_formset))


# class ContentCreateUpdateView(TemplateResponseMixin, View):
#     module = None
#     model = None
#     obj = None
#     template_name = 'courses/manage/content/form.html'
#
#     def get_model(self, model_name):
#         if model_name in ['text', 'video', 'image', 'file', 'question']:
#             return apps.get_model(app_label='courses', model_name=model_name)
#         return None
#
#     def get_form(self, model, *args, **kwargs):
#         Form = modelform_factory(model, exclude=['owner', 'order', 'created', 'updated'])
#         return Form(*args, **kwargs)
#
#     def dispatch(self, request, module_id, model_name, id=None):
#         self.module = get_object_or_404(Module, id=module_id, course__owner=request.user)
#         self.model = self.get_model(model_name)
#         if id:
#             self.obj = get_object_or_404(self.model, id=id, owner=request.user)
#
#         return super(ContentCreateUpdateView, self).dispatch(request, module_id, model_name, id)
#
#     def get(self, request, module_id, model_name, id=None):
#         form = self.get_form(self.model, instance=self.obj)
#         if model_name == 'question':
#             question_choices_formset = QuestionChoicesFormSet(instance=self.obj)
#         return self.render_to_response({'form': form, 'object': self.obj, 'question_choices_formset': question_choices_formset})
#
#     def post(self, request, module_id, model_name, id=None):
#         form = self.get_form(self.model, instance=self.obj, data=request.POST, files=request.FILES)
#
#         if model_name == 'question':
#             question_choices_formset = QuestionChoicesFormSet(instance=self.obj, data=request.POST)
#             if question_choices_formset.is_valid():
#                 print('---Valid---')
#
#         if form.is_valid():
#             obj = form.save(commit=False)
#             obj.owner = request.user
#             obj.save()
#
#             if not id:
#                 # new content
#                 Content.objects.create(module=self.module, item=obj)
#                 return redirect('module_content_list', self.module.id)
#
#         return self.render_to_response({'form': form, 'object': self.obj})


class ContentDeleteView(OwnerCourseEditMixin, View):
    def post(self, request, id):
        content = get_object_or_404(Content, id=id, module__course__owner=request.user)
        module = content.module
        content.item.delete()
        content.delete()
        return redirect('module_content_list', module.id)


class ModuleContentListView(OwnerCourseEditMixin, TemplateResponseMixin, View):
    template_name = 'courses/manage/module/content_list.html'

    def get(self, request, module_id):
        module = get_object_or_404(Module, id=module_id, course__owner=request.user)
        return self.render_to_response({'module': module})


class ModuleOrderView(CsrfExemptMixin, OwnerCourseEditMixin, JsonRequestResponseMixin, View):
    def post(self, request):
        for id, order in self.request_json.items():
            Module.objects.filter(id=id, course__owner=request.user).update(order=order)
        return self.render_json_response({'saved': 'OK'})

class ContentOrderView(CsrfExemptMixin, OwnerCourseEditMixin, JsonRequestResponseMixin, View):
    def post(self, request):
        for id, order in self.request_json.items():
            Content.objects.filter(id=id, module__course__owner=request.user).update(order=order)
        return self.render_json_response({'saved': 'OK'})

class CourseListView(TemplateResponseMixin, View):
    model = Course
    template_name = 'courses/course/list.html'

    def get(self, request, subject=None):
        subjects = cache.get('all_subjects')
        if not subjects:
            subjects = Subject.objects.annotate(total_courses=Count('courses'))
            cache.set('all_subjects', subjects)

        all_courses = Course.objects.annotate(total_modules=Count('modules'))
        if subject:
            subject = get_object_or_404(Subject, slug=subject)
            key = 'subject_{}_courses'.format(subject.id)
            courses = cache.get(key)
            if not courses:
                courses = all_courses.filter(subject=subject)
                cache.set(key, courses)
        else:
            courses = cache.get('all_courses')
            if not courses:
                courses = all_courses
                cache.set('all_courses', courses)

        return self.render_to_response({'subjects': subjects, 'subject': subject, 'courses': courses})


class CourseDetailView(DetailView):
    model = Course
    template_name = 'courses/course/detail.html'

    def get_context_data(self, **kwargs):
        context = super(CourseDetailView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            is_enrolled = StudentEnrollment.objects.filter(course=self.get_object(), student=self.request.user).exists()
            context['enroll_form'] = CourseEnrollForm(initial={'course':self.object})
            context['is_enrolled'] = is_enrolled
        return context

@require_http_methods(["POST"])
def recive_student_answer(request):
    if request.is_ajax():
        question = Question.objects.get(id=request.POST.get('question_id'))
        student_choice = question.choices.get(id=request.POST.get('id'))
        right_choice = question.choices.get(is_right_choice=True)

        is_right = False
        if student_choice == right_choice:
            is_right = True

        StudentQuestionAnswer.objects.update_or_create(student=request.user, question=question, defaults={'is_right': is_right})
        return JsonResponse({'is_right': is_right, 'right_choice_id': right_choice.id})

@require_http_methods(["POST"])
def save_student_progress(request):
    if request.is_ajax():
        student = request.user
        module = Module.objects.get(id=request.POST.get('module_id'))
        for content in module.contents.all():
            StudentLearningProgress.objects.filter(content=content, enrollment__student=student).update(is_finish=True, finish_time=timezone.now())

        return JsonResponse({'status': 'ok'})

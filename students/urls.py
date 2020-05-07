from django.urls import path
from . import views
#from django.views.decorators.cache import cache_page

urlpatterns = [
    #path('register/', views.signup, name='student_registration'),
    path('enroll-course/', views.StudentEnrollCourseView.as_view(), name='student_enroll_course'),
    path('courses/', views.StudentCourseListView.as_view(), name='student_course_list'),
    path('course/<pk>/', views.StudentCourseDetailView.as_view(), name='student_course_detail'),
    path('course/<pk>/<module_id>/', views.StudentCourseDetailView.as_view(), name='student_course_detail_module'),
    path('course/<pk>/<module_id>/<content_id>/', views.StudentCourseDetailView.as_view(), name='student_course_detail_module_content'),

    #path('course/<course_id>/<module_id>/<content_id>/', views.StudentCourseModuleContentDetailView.as_view(), name='student_course_detail_module_content'),

    # path('course/<pk>/', cache_page(60 * 15)(views.StudentCourseDetailView.as_view()), name='student_course_detail'),
    # path('course/<pk>/<module_id>/', cache_page(60 * 15)(views.StudentCourseDetailView.as_view()), name='student_course_detail_module'),
]

from django.urls import path, include
from . import views
from rest_framework import routers

app_name = 'courses'

router = routers.DefaultRouter()
router.register('courses', views.CourseViewSet)
router.register('subjects', views.SubjectViewSet)

urlpatterns = [
    # path('subjects/', views.SubjectListView.as_view(), name='subject_list'),
    # path('subjects/<pk>/', views.SubjectDetailView.as_view(), name='subject_detail'),
    # path('courses/', views.CourseListView.as_view(), name='course_list'),
    # path('courses/<pk>/', views.CourseDetailView.as_view(), name='course_detail'),
    # path('courses/<pk>/enroll/', views.CourseEnrollView.as_view(), name='course_enroll'),
    path('', include(router.urls)),
]

from django.urls import path, include
from django.conf.urls import url
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('ajax/email_check/', views.email_check, name='email_check'),
    url(r'^confirm-email/(?P<uuid>[a-z0-9\-]+)/', views.verify, name='verify'),
]

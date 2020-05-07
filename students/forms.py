from django import forms
from courses.models import Course
from .models import StudentEnrollment


class CourseEnrollForm(forms.ModelForm):
    course = forms.ModelChoiceField(queryset=Course.objects.all(), widget=forms.HiddenInput)
    class Meta:
        model = StudentEnrollment
        fields = {'course'}

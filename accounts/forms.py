from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import Profile

class SignupForm(forms.ModelForm):
    username = forms.CharField(max_length = 100, required = True)
    password = forms.CharField(widget = forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    instructor_flag = forms.BooleanField(required=False)
    field_order = ['first_name', 'last_name', 'username', 'email', 'password', 'confirm_password', 'instructor_flag']

    class Meta:
        model = User
        fields = {'first_name', 'last_name', 'username', 'email', 'password', 'confirm_password', 'instructor_flag'}

    def clean(self):
        super(SignupForm, self).clean()
        first_name = self.cleaned_data.get('first_name')
        last_name = self.cleaned_data.get('last_name')
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords does not match")

        if not first_name.isalpha():
            self._errors['first_name'] = self.error_class(['Please enter correct first name. Use only alphabetical characters (a-z, A–Z)'])

        if not last_name.isalpha():
            self._errors['last_name'] = self.error_class(['Please enter correct last name. Use only alphabetical characters (a-z, A–Z)'])

        try:
            validate_password(password)
        except forms.ValidationError as e:
            raise forms.ValidationError("Password")

        del self.cleaned_data['confirm_password']
        return self.cleaned_data

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields=('image',)

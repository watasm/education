from django.shortcuts import render, redirect
from django.contrib.auth.models import User, Group
from django.views.generic.base import TemplateResponseMixin, View
from .forms import SignupForm, ProfileForm
from django.contrib.auth import authenticate, login
from django.http import JsonResponse

from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import Profile
from .tasks import send_verification_email
from django.http import HttpResponseNotFound

@receiver(post_save, sender=Profile)
def profile_post_save(sender, instance, signal, *args, **kwargs):
    if not instance.is_verified:
        send_verification_email.delay(instance.pk)

class SignupView(TemplateResponseMixin, View):
    template_name = 'registration/signup.html'

    def get(self, request):
        form = SignupForm()
        profile_form = ProfileForm()
        return render(request, self.template_name, {'form': form, 'profile_form': profile_form})
        #return self.render_to_response({'form': form, 'profile_form': profile_form})

    def post(self, request):
        form = SignupForm(request.POST)
        profile_form = ProfileForm(request.POST, request.FILES)
        if form.is_valid() and profile_form.is_valid():
            cd = form.cleaned_data
            instructor_flag = cd['instructor_flag']
            # delete instructor flag for create new user
            del cd['instructor_flag']
            user = User.objects.create_user(**cd)

            profile = profile_form.save(commit = False)
            profile.user = user
            profile.save()
            profile_form.save_m2m()

            login(request, authenticate(
                username = form.cleaned_data['username'],
                password = form.cleaned_data['password'],
            ))

            # Check if is instructor_flag True, add to group Instructors
            if instructor_flag:
                instructors = Group.objects.get(name='Instructors')
                instructors.user_set.add(user)

            return redirect('student_course_list')
        return render(request, self.template_name, {'form': form, 'profile_form': profile_form})
        #return self.render_to_response({'form': form})

def verify(request, uuid):
    try:
        profile = Profile.objects.get(verification_uuid=uuid, is_verified=False, user=request.user)
    except Profile.DoesNotExist:
        return HttpResponseNotFound("User does not exist or is already verified", status=404)

    profile.is_verified = True
    profile.save()
    return redirect('/')

def email_check(request):
    if request.is_ajax():
        email = request.POST.get('email')
        if User.objects.filter(email=email):
            return JsonResponse({'status': 'ok'})
        else:
            return JsonResponse({'status': 'ko'})

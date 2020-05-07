from django.db import models
from django.contrib.auth.models import User
from courses.models import Course, Content

class StudentEnrollment(models.Model):
    student = models.ForeignKey(User, related_name='courses_joined', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name='students', on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['student', 'course']

    def __str__(self):
        return '{} enroll course {}'.format(self.student.username, self.course.title)


class StudentLearningProgress(models.Model):
    enrollment = models.ForeignKey(StudentEnrollment, on_delete=models.CASCADE, related_name='student_learning_progress')
    content = models.ForeignKey(Content, on_delete=models.CASCADE, related_name='learning_progress')
    start_time = models.DateTimeField(auto_now_add=True)
    finish_time = models.DateTimeField(auto_now=True)
    is_finish = models.BooleanField(default=False)

    class Meta:
        unique_together = ['enrollment', 'content']

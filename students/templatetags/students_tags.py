from django import template
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from courses.models import Question, QuestionChoices
from random import shuffle

register = template.Library()


@register.simple_tag
def is_learned(student, content):
    try:
        process = content.learning_progress.get(content=content, enrollment__student = student)
        if process.is_finish:
            return 'Finished'
        else:
            return 'In process'
    except ObjectDoesNotExist:
        return 'Not started'

@register.inclusion_tag('courses/content/question_choices_section.html')
def get_choices(question):
    print('yes')
    choices = list(question.choices.all())
    shuffle(choices)
    return {'choices': choices, 'question_id': question.id}

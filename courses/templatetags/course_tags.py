from django import template
from courses.forms import QuestionAnswerForm

register = template.Library()

@register.filter
def model_name(obj):
    try:
        return obj._meta.model_name

    except AttributeError:
        return None

# @register.inclusion_tag('courses/content/question_answer_form_section.html', takes_context=True)
# def create_question_answer_form(context, question):
#     print(context['request'])
#     #question_answer_form = QuestionAnswerForm(question=question)
#     return {}

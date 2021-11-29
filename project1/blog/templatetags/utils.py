# custom template tags
from django import template

register = template.Library()

@register.simple_tag
def current_user():
    return False

# @register.simple_tag
# def current_user(request: HttpRequest):
#     return request.session.get("user")

# # custom filters
# from django.template.Library import register

# @register.filter(name="loggedin")
# def loggedin(user):
#     pass

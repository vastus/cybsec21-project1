from pprint import pprint
# custom template tags
from django import template

register = template.Library()


@register.simple_tag
def has_role():
    return True


# @register.simple_tag
# def current_user():
#     return False

# @register.simple_tag
# def current_user(request: HttpRequest):
#     return request.session.get("user")

# # custom filters
# from django.template.Library import register

# @register.filter(name="loggedin")
# def loggedin(user):
#     pass

@register.filter
def is_a(user: dict, role: str):
    return True

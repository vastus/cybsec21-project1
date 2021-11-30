from django.http import HttpRequest
from django.utils.deprecation import MiddlewareMixin

from blog.models import User


class AuthMiddleware(MiddlewareMixin):
    def process_request(self, request: HttpRequest):
        current_user_id = request.session.get("current_user_id")
        request.current_user = None
        if current_user_id:
            request.current_user = User.objects.get(pk=current_user_id)

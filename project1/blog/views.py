from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from .models import User

CURRENT_USER = "current_user"

def _render(request: HttpRequest, templ: str, context: dict = {}):
    context[CURRENT_USER] = request.session.get(CURRENT_USER)
    return render(request, templ, context)


@require_http_methods(["GET"])
def index(request: HttpRequest):
    return _render(request, "blog/index.html")


@require_http_methods(["GET", "POST"])
def login(request: HttpRequest):
    if request.session.get(CURRENT_USER):
        return redirect("/")
    if request.method == "GET":
        return _render(request, "blog/login.html")
    return _handle_login(request)


def _handle_login(request: HttpRequest):
    email = request.POST["login_email"]
    password = request.POST["login_password"]
    user, failure = User.authenticate(email, password)
    if user:
        request.session[CURRENT_USER] = user.to_json()
        return redirect("/")
    context = {"failure": failure}
    return _render(request, "blog/login.html", context)


def logout(request):
    request.session[CURRENT_USER] = None
    return redirect("/")


@require_http_methods(["GET", "POST"])
def register(request: HttpRequest):
    if request.method == "GET":
        return _render(request, "blog/register.html")
    return _handle_registration(request)


def _handle_registration(request: HttpRequest):
    email = request.POST["registration_email"]
    password = request.POST["registration_password"]
    ok, failure = User.register(email, password)
    if ok:
        return redirect("/login")
    context = {"failure": failure}
    return _render(request, "blog/register.html", context)


@require_http_methods(["GET"])
def new_post(request: HttpRequest):
    user = request.session.get(CURRENT_USER)
    if not user:
        return redirect("/login")
    return _render(request, "blog/posts/new.html")


@require_http_methods(["POST"])
def create_post(request: HttpRequest):
    title = request.POST["post_title"]
    content = request.POST["content"]
    post = Post(title, content)
    post.save()

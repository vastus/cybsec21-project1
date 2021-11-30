from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from .models import PostForm, User

CURRENT_USER_ID = "current_user_id"


def _render(request: HttpRequest, templ: str, context: dict = {}):
    # current_user_id = request.session.get(CURRENT_USER_ID)
    # if current_user_id:
    #     request.current_user = User.objects.get(pk=current_user_id)
    return render(request, templ, context)


@require_http_methods(["GET"])
def index(request: HttpRequest):
    return _render(request, "blog/index.html")


@require_http_methods(["GET", "POST"])
def login(request: HttpRequest):
    if request.current_user:
        return redirect("/")
    if request.method == "GET":
        return _render(request, "blog/login.html")
    return _handle_login(request)


def _handle_login(request: HttpRequest):
    # import pdb; pdb.set_trace()
    email = request.POST["login_email"]
    password = request.POST["login_password"]
    user, failure = User.authenticate(email, password)
    if user:
        request.session[CURRENT_USER_ID] = user.id
        return redirect("/")
    context = {"failure": failure}
    return _render(request, "blog/login.html", context)


def logout(request):
    request.session[CURRENT_USER_ID] = None
    return redirect("/")


@require_http_methods(["GET", "POST"])
def register(request: HttpRequest):
    if request.method == "GET":
        return _render(request, "blog/register.html")
    return _handle_registration(request)


def _handle_registration(request: HttpRequest):
    email = request.POST["registration_email"]
    email_confirmation = request.POST["registration_email_confirmation"]
    password = request.POST["registration_password"]

    if email != email_confirmation:
        context = {"failure": "emails must match"}
        return _render(request, "blog/register.html", context)

    ok, failure = User.register(email, password)
    if ok:
        return redirect("/login")
    context = {"failure": failure}
    return _render(request, "blog/register.html", context)


@require_http_methods(["GET"])
def new_post(request: HttpRequest):
    if not request.current_user:
        return redirect("/login")
    return _render(request, "blog/posts/new.html")


@require_http_methods(["POST"])
def create_post(request: HttpRequest):
    # title = request.POST["post_title"]
    # content = request.POST["post_content"]
    # import pdb; pdb.set_trace()
    form = PostForm({**request.POST, 'user': request.current_user})#, "user": request.current_user})
    if not form.is_valid():
        messages.error(request, form.errors)
        return _render(request, "blog/posts/new.html")
    post = form.save()
    return redirect(reverse("show_post", args=[post.id]))


@require_http_methods(["GET"])
def show_post(request: HttpRequest, post_id: int):
    return HttpResponse(f"post_id={post_id}")

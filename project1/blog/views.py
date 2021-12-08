from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from .models import Post, PostForm, User, ProfileForm

CURRENT_USER_ID = "current_user_id"


def _render(request: HttpRequest, templ: str, context: dict = {}):
    return render(request, templ, context)


@require_http_methods(["GET"])
def index(request: HttpRequest):
    posts = []
    q = request.GET.get("q")
    if q:
        sql = f"""
        select * from blog_post \
        where title like '%{q}%' \
        or content like '%{q}%' \
        """
        posts = Post.objects.raw(sql)
    else:
        posts = Post.objects.all()
    return _render(request, "blog/index.html", {"posts": posts})


@require_http_methods(["GET", "POST"])
def login(request: HttpRequest):
    if request.current_user:
        return redirect("/")
    if request.method == "GET":
        return _render(request, "blog/login.html")
    return _handle_login(request)


def _handle_login(request: HttpRequest):
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
    username = request.POST["registration_username"]
    email = request.POST["registration_email"]
    email_confirmation = request.POST["registration_email_confirmation"]
    password = request.POST["registration_password"]

    if email != email_confirmation:
        context = {"failure": "emails must match"}
        return _render(request, "blog/register.html", context)

    ok, failure = User.register(username, email, password)
    if ok:
        return redirect("/login")
    context = {"failure": failure}
    return _render(request, "blog/register.html", context)


@require_http_methods(["GET", "POST"])
def profile(request: HttpRequest, user_id: int):
    if request.method == 'GET':
        user = User.objects.get(pk=user_id)
        return _render(request, "blog/profile.html", {'user': user})
    form = ProfileForm(request.POST)
    user = User.objects.get(pk=user_id)
    if form.is_valid():
        user.email = form.cleaned_data['email']
        user.save()
        return redirect(reverse("profile", args=[user.id]))
    messages.error(request, form.errors)
    return _render(request, "blog/profile.html", {'user': user})


@require_http_methods(["GET"])
def new_post(request: HttpRequest):
    if not request.current_user:
        return redirect("/login")
    return _render(request, "blog/posts/new.html")


@require_http_methods(["POST"])
def create_post(request: HttpRequest):
    title = request.POST["title"]
    content = request.POST["content"]
    form = PostForm({"title": title, "content": content, "user": request.current_user})
    if form.is_valid():
        post = form.save()
        return redirect(reverse("show_post", args=[post.id]))
    messages.error(request, form.errors)
    return _render(request, "blog/posts/new.html")


@require_http_methods(["GET"])
def show_post(request: HttpRequest, post_id: int):
    post = Post.objects.get(pk=post_id)
    comments = post.comment_set.order_by("-inserted_at").all
    return _render(
        request, "blog/posts/show.html", {"post": post, "comments": comments}
    )


@require_http_methods(["POST"])
def create_comment(request: HttpRequest, post_id: int):
    post = Post.objects.get(pk=post_id)
    post.comment_set.create(
        body=request.POST["comment_body"], user_id=request.POST["comment_user_id"]
    )
    return redirect(reverse("show_post", args=[post.id]))

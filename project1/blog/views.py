from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from .models import User


@require_http_methods(['GET'])
def index(request: HttpRequest):
    return render(request, "blog/index.html", {"user": request.session.get("user")})


@require_http_methods(["GET", "POST"])
def login(request: HttpRequest):
    if request.method == "GET":
        return render(request, "blog/login.html")
    return _handle_login(request)


def _handle_login(request: HttpRequest):
    email = request.POST["login_email"]
    password = "passu"
    # password = request.POST["login_password"]
    user, failure = User.authenticate(email, password)
    if user:
        request.session["user"] = user.to_json()
        return redirect("/")
    context = {"failure": failure}
    return render(request, "blog/login.html", context)


@require_http_methods(['GET'])
def new_post(request: HttpRequest):
    user = request.session.get("user")
    if not user:
        return redirect("/login")
    return render(request, "blog/posts/new.html", {"user": user})

@require_http_methods(['POST'])
def create_post(request: HttpRequest):
    title = request.POST["post_title"]
    content = request.POST["content"]
    post = Post(title, content)
    post.save()
    

from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login, name="login"),
    path("logout", views.logout, name="logout"),
    path("register", views.register, name="register"),
    path("profile/<int:user_id>", views.profile, name="profile"),

    path("posts", views.create_post, name="create_post"),
    path("posts/new", views.new_post, name="new_post"),
    path("posts/<int:post_id>", views.show_post, name="show_post"),
    path("posts/<int:post_id>/comments", views.create_comment, name="create_comment"),
]

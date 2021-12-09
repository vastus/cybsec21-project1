import hashlib
import os

from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.db import models
from django.forms import Form, ModelForm
from django import forms

AUTHOR = 0b0010
ADMIN = 0b1111


def encrypt_password(password: str, salt: bytes):
    return hashlib.scrypt(bytes(password, "utf-8"), salt=salt, n=128, r=1024, p=16)


class User(models.Model):
    username = models.CharField(max_length=64, null=False, blank=False)
    email = models.EmailField(unique=True)
    role = models.PositiveIntegerField(null=False, default=0)
    password_hash = models.BinaryField(null=False, blank=False)
    password_salt = models.BinaryField(null=False, blank=False)

    def to_json(self):
        fields = ("email",)
        return {field: getattr(self, field) for field in fields}

    @property
    def is_author(self):
        return (self.role & AUTHOR) != 0

    @classmethod
    def authenticate(cls, email, password):
        user = cls.objects.filter(email=email).first()
        if not user:
            return None, "incorrect email and/or password"

        hashed_password = encrypt_password(password, user.password_salt)
        if hashed_password != user.password_hash:
            return None, "incorrect email and/or password"

        return user, ""

    @classmethod
    def register(cls, username, email, password):
        user = cls.objects.filter(email=email).first()
        if user:
            return False, "username/email already in use"
        user = cls.objects.filter(username=username).first()
        if user:
            return False, "username/email already in use"
        password_salt = os.urandom(128)
        password_hash = encrypt_password(password, password_salt)
        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            password_salt=password_salt,
        )

        try:
            user.full_clean()
        except ValidationError as e:
            return False, e.message

        user.save()
        return True, ""


class Post(models.Model):
    title = models.TextField(null=False)
    content = models.TextField(null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ["title", "content", "user"]


class Comment(models.Model):
    body = models.TextField()
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    inserted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ProfileForm(forms.ModelForm):
    email_confirmation = forms.EmailField()

    class Meta:
        model = User
        fields = ["email"]

    def clean(self):
        data = super().clean()
        email = data.get("email")
        email_confirmation = data.get("email_confirmation")
        if email != email_confirmation:
            raise ValidationError(
                "Email and email confirmation must match", code="mismatch"
            )

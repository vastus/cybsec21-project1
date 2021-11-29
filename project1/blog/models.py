from django.core.validators import MinLengthValidator
from django.db import models
from django.forms import ModelForm


class User(models.Model):
    email = models.CharField(max_length=256)

    def to_json(self):
        fields = ("email",)
        return {field: getattr(self, field) for field in fields}

    @classmethod
    def authenticate(cls, email, password):
        user = cls.objects.filter(email=email).first()
        if not user:
            return None, "user not found"
        # if password != user.password:
        #     return None, "wrong password"
        return user, ""


class Post(models.Model):
    title = models.TextField(null=False)
    content = models.TextField(null=False)


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ["title", "content"]

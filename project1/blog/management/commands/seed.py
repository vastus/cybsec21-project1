from random import randint
from typing import Optional

from django.core.management.base import BaseCommand, CommandError
from faker import Faker

from blog.models import *

fake = Faker()


class Command(BaseCommand):
    help = "Seed the DB"

    def handle(self, *args, **options):
        admin_email = "admin@lo.co"
        author_email = "jo@nes.bo"
        testos_email = "testos@teroni.fi"

        users = (
            ("sudo", admin_email, "AdminPass99"),
            ("Jo Nesbo", author_email, "AuthorPass99"),
            ("Testos Teroni", testos_email, "TestosPass99"),
        )

        for username, email, password in users:
            ok, err = User.register(username, email, password)
            if not ok:
                raise CommandError(err)

        admin = User.objects.get(email=admin_email)
        author = User.objects.get(email=author_email)
        testos = User.objects.get(email=testos_email)

        admin.role = ADMIN
        admin.save()
        author.role = AUTHOR
        author.save()

        posts = (
            Post(title=fake.sentence(), content=content(), user=admin),
            Post(title=fake.sentence(), content=content(), user=author),
            Post(title=fake.sentence(), content=content(), user=author),
        )

        for post in posts:
            post.full_clean()
            post.save()

        for post in Post.objects.all():
            gen_comments(post)


def content(num_paras=8):
    return " ".join(fake.paragraphs(num_paras))


def gen_comments(post: Post, amount_range=(1,17)):
    for _ in range(randint(*amount_range)):
        email = fake.email()
        ok, err = User.register(
            username=fake.user_name(), email=email, password=fake.password()
        )
        if not ok:
            raise CommandError(err)
        user = User.objects.get(email=email)
        body = ' '.join(fake.sentences(randint(1, 11)))
        Comment.objects.create(post=post, user=user, body=body)

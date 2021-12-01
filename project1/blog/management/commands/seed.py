from django.core.management.base import BaseCommand, CommandError
from faker import Faker

from blog.models import *

fake = Faker()


class Command(BaseCommand):
    help = "Seed the DB"

    def handle(self, *args, **options):
        admin_email = "admin@local"
        author_email = "jo@nesbo"
        testos_email = "testos@teroni"

        users = (
            (admin_email, "AdminPass99"),
            (author_email, "AuthorPass99"),
            (testos_email, "TestosPass99"),
        )

        for email, password in users:
            ok, err = User.register(email, password)
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

        # comments


def content(num_paras=8):
    return " ".join(fake.paragraphs(num_paras))



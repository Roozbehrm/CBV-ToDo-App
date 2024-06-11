from django.core.management.base import BaseCommand
from faker import Faker
import random
from accounts.models import User, Profile
from todo.models import Task


class Command(BaseCommand):
    help = "Inserting dummy data"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fake = Faker()

    def handle(self, *args, **options):
        user = User.objects.create_user(
            email=self.fake.email(),
            password="!@#12345",
            is_verified=random.choice([True, False]),
        )
        profile = Profile.objects.get(user=user)
        profile.first_name = self.fake.first_name()
        profile.last_name = self.fake.last_name()
        profile.save()

        for _ in range(5):
            Task.objects.create(
                profile=profile,
                title=self.fake.sentence(nb_words=3),
                description=self.fake.paragraph(nb_sentences=5),
                done=random.choice([True, False]),
            )

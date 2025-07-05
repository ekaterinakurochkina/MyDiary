from django.core.management import BaseCommand

from users.models import User


class Command(BaseCommand):
    """ Команда для создания суперюзера """
    def handle(self, *args, **options):
        user = User.objects.create(email='katifedr@mail.ru', display_name='superuser', is_staff=True, is_superuser=True)
        user.set_password('admin')
        user.save()

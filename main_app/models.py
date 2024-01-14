from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

import re

from .validators import validate_color_layout, validate_team_layout

# Create your models here.


class User(AbstractUser):
    """
    Extension of a stock Django user model.
    It allows storing additional user info without using any ForeignKey.
    """
    rooms_layout = models.TextField(
        blank=True,
        verbose_name='Коды комнат для работы',
        help_text='По одному в отдельной строке',
    )


class Contest(models.Model):
    """
    A model to store information about ongoing contests.
    """
    class TestSystem(models.IntegerChoices):
        """
        Enum made to make test system info storing more readable.
        """
        YANDEX_CONTEST = 1, _("Яндекс.Контест")
        CODEFORCES = 2, _("Codeforces")

    external_id = models.IntegerField(
        verbose_name="Внешний ID контеста",
    )
    test_system = models.IntegerField(
        choices=TestSystem.choices,
        verbose_name="Тестирующая система",
    )
    api_key = models.CharField(
        max_length=250,
        verbose_name="API-ключ для доступа к соревнованию",
    )
    api_secret = models.CharField(
        max_length=250,
        blank=True,
        verbose_name="API-секрет, если требуется",
    )

    colors_layout = models.TextField(
        blank=False,
        validators=[validate_color_layout],
        verbose_name="Распределение цветов шариков по задачам",
        help_text='В формате "ИндексЗадачи=Цвет", по одной записи в строке',
    )
    teams_layout = models.TextField(
        blank=False,
        validators=[validate_team_layout],
        verbose_name="Распределение команд по местам",
        help_text='В формате "ЛогинКоманды:ПомещениеКоманды:НомерМестаКоманды:НазваниеКоманды", '
                  'по одной записи в строке',
    )
    admin = models.ForeignKey(
        'User',
        on_delete=models.PROTECT,
        related_name='contests',
        related_query_name='contest',
        verbose_name='Администратор контеста',
    )

    @property
    def test_system_label(self):
        """
        A simple shortcut to retrieve enum label easily.
        """
        return self.TestSystem(self.test_system).label

    def __str__(self):
        return f"{self.test_system_label} {self.external_id}"

    class Meta:
        verbose_name = "контест"
        verbose_name_plural = "контесты"


class Submission(models.Model):
    """
    A model to cache information about all actual participants' submissions.
    """
    class Verdict(models.IntegerChoices):
        """
        Enum made to make verdict info storing more readable.
        """
        TESTING = 1, _("Тестируется")
        OK = 2, _("Полное решение")
        OTHER = 3, _("Иной вердикт")

    external_id = models.BigIntegerField(
        verbose_name="Внешний ID посылки",
    )
    contest = models.ForeignKey(
        'Contest',
        on_delete=models.PROTECT,
        related_name='submissions',
        related_query_name='submission',
        verbose_name='Контест',
    )
    problem_index = models.CharField(
        max_length=10,
        verbose_name='Индекс задачи',
        help_text='Обычно буква или цифра, реже комбинация букв',
    )
    author = models.CharField(
        max_length=100,
        verbose_name="Никнейм участника",
    )
    time_from_start = models.IntegerField(
        verbose_name="Время от начала контеста до попытки (в секундах)",
    )
    verdict = models.IntegerField(
        choices=Verdict.choices,
        verbose_name="Вердикт посылки",
    )

    def __str__(self):
        return f"{self.contest.test_system_label} {self.contest.external_id} | {self.external_id}"

    class Meta:
        verbose_name = "посылка"
        verbose_name_plural = "посылки"


class Order(models.Model):
    """
    A model to store information about all actual balloon delivery orders.
    """
    submission = models.OneToOneField(
        'Submission',
        on_delete=models.PROTECT,
        related_name='order',
        related_query_name='order',
        verbose_name='Посылка',
    )
    balloon_color = models.CharField(
        max_length=250,
        blank=True,
        verbose_name='Цвет шарика',
    )
    room = models.CharField(
        max_length=250,
        blank=True,
        verbose_name='Локация участника',
        help_text='Обычно комната или зал',
    )
    place = models.CharField(
        max_length=250,
        blank=True,
        verbose_name='Номер стола участника',
    )
    author_name = models.CharField(
        max_length=250,
        blank=True,
        verbose_name='Имя участника',
        help_text='Если команда - то название команды',
    )
    volunteer = models.ForeignKey(
        'User',
        on_delete=models.PROTECT,
        related_name='orders',
        related_query_name='order',
        verbose_name='Волонтёр',
    )
    done = models.BooleanField(
        default=False,
        blank=True,
        verbose_name="Ордер закрыт",
    )

    @classmethod
    def create_order_for_submission(cls, submission: Submission):
        """
        A function to construct an order by a submission. Handles corner-cases.
        """
        order = Order(submission=submission)
        author = submission.author

        color_metadata_found = False
        for line in submission.contest.colors_layout.splitlines():
            matches = re.findall(rf'^({submission.problem_index})=([\w#]+)', line)
            if matches:
                match = matches[0]
                order.balloon_color = match[1]
                color_metadata_found = True
                break
        location_metadata_found = False
        for line in submission.contest.teams_layout.splitlines():
            matches = re.findall(rf'^({author}):(\w+):(\w+):(.+)$', line)
            if matches:
                match = matches[0]
                order.room = match[1]
                order.place = match[2]
                order.author_name = match[3]
                location_metadata_found = True
                break
        if not (color_metadata_found and location_metadata_found):
            order.volunteer = submission.contest.admin  # Invalid data in layout, falling back to admin
            return order.save()

        volunteers = User.objects.filter(
            rooms_layout__regex=rf'(?:^|[\n\r\u2028\u2029]){order.room}(?:$|[\n\r\u2028\u2029])',
        ).annotate(num_orders=models.Count('order')).order_by('num_orders')
        if volunteers.count() == 0:
            order.volunteer = submission.contest.admin  # No volunteer found, falling back to admin
        else:
            order.volunteer = volunteers.first()
        return order.save()

    def __str__(self):
        return f"Ордер ({self.submission})"

    class Meta:
        verbose_name = "ордер"
        verbose_name_plural = "ордера"

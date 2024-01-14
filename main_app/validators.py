from django.core.exceptions import ValidationError
import re


def validate_color_layout(value: str) -> str:
    """
    Validates that a given color layout is well-formed.
    """
    for line in value.splitlines():
        if not re.fullmatch(r'^\w+=[\w#]+$', line):
            raise ValidationError(f'Строка "{line}" не соответствует формату "ИндексЗадачи=Цвет"')
    return value


def validate_team_layout(value: str) -> str:
    """
    Validates that a given team layout is well-formed.
    """
    for line in value.splitlines():
        if not re.fullmatch(r'^[\w=]+:\w+:\w+:.+$', line):
            raise ValidationError(f'Строка "{line}" не соответствует формату '
                                  f'"ЛогинКоманды:ПомещениеКоманды:НомерМестаКоманды:НазваниеКоманды"')
    return value

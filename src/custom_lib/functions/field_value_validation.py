from django.core.exceptions import ValidationError


def gt_zero_validator(value):
    if value <= 0:
        raise ValidationError('Value must be greater than zero')
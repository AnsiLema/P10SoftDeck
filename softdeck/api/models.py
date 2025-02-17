from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from datetime import date

def validate_age(birth_date):
    """
    Validates if the user's age is at least 15 years old based on their birth_date.
    If the age is less than 15, a ValidationError is raised.

    :param birth_date: The birth_date of the user as a `datetime.date` object.
    :type birth_date: datetime.date
    :raises ValidationError: If the user's age is less than 15.
    :return: None
    """
    today = date.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    if age < 15:
        raise ValidationError(_("L'utilisateur doit avoir au moins 15 ans."))

class CustomUser(AbstractUser):
    """
    Represents a custom user extending the default Django AbstractUser.

    This class provides additional fields and validation to the standard
    Django user model, allowing customization for specific application needs.

    :ivar birth_date: The date of birth of the user. This field is optional and
        validated to ensure the user's age meets the specified criteria.
    :type birth_date: models.DateField
    :ivar can_be_contacted: Indicates whether the user has consented to be
        contacted. Defaults to False.
    :type can_be_contacted: models.BooleanField
    :ivar can_data_be_shared: Specifies whether the user's data can be shared.
        Defaults to False.
    :type can_data_be_shared: models.BooleanField
    """
    birth_date = models.DateField(validators=[validate_age], null=True, blank=True)
    can_be_contacted = models.BooleanField(default=False)
    can_data_be_shared = models.BooleanField(default=False)

    def __str__(self):
        return self.username
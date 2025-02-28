from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from datetime import date
from django.conf import settings
import uuid


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

    def clean(self):
        if self.birth_date:
            validate_age(self.birth_date)  # Extra Validation

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username


class Project(models.Model):
    TYPE_CHOICES = [
        ("BACKEND", "Back-end"),
        ("FRONTEND", "Front-end"),
        ("IOS", "iOS"),
        ("ANDROID", "Android")
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="owned_projects")

    def __str__(self):
        return self.title


class Contributor(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="contributors")

    class Meta:
        unique_together = ("user", "project")

    def __str__(self):
        return f"{self.user.username} → ({self.project.title})"


class Issue(models.Model):
    PRIORITY_CHOICES = [
        ("LOW", "Low"),
        ("MEDIUM", "Medium"),
        ("HIGH", "High")
    ]
    TAG_CHOICES = [
        ("BUG", "Bug"),
        ("FEATURE", "Feature"),
        ("TASK", "Task")
    ]
    STATUS_CHOICES = [
        ("TODO", "To do"),
        ("IN_PROGRESS", "In progress"),
        ("FINISHED", "Finished")
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    tag = models.CharField(max_length=10, choices=TAG_CHOICES)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="TODO")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="issues")
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE,
                                    related_name="assigned_issues")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="created_issues")
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title}, créé le ({self.created_time})"


class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    description = models.TextField(blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="created_comments")
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name="comments")
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Commentaire de {self.author.username} sur l'issue {self.issue.title}"

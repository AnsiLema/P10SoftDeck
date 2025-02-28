from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import Project


class IsAuthorOrReadOnly(BasePermission):
    """
    Provides permission logic to allow read-only access to all users and
    restrict write permissions exclusively to the author of the object.

    This permission class is suitable for scenarios where authenticated
    users can read or retrieve any object, but only the author can modify
    or delete it.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.author == request.user


class IsContributor(BasePermission):
    """
    Custom permission class to check if a user is a contributor to a given project.

    The purpose of this class is to ensure access control by allowing actions only to users
    who are contributors of a specified project. The permission is determined based on the
    `project_pk` obtained from the view's keyword arguments and checks the existence of
    an association between the user and the project in the Contributor model.
    """
    def has_object_permission(self, request, view, obj):
        # Only users who are contributors to the project can access it.
        return request.user in [contributor.user for contributor in obj.contributors.all()]


class IsProjectAuthor(BasePermission):
    def has_permission(self, request, view):
        project_id = view.kwargs.get("project_pk")
        project = Project.objects.filter(id=project_id).first()
        return project and project.author == request.user

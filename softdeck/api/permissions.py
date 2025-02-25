from rest_framework.permissions import BasePermission
from .models import Contributor, Project


class IsAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user

    def has_permission(self, request, view):
        project_id = view.kwargs.get('pk')
        if project_id:
            project = Project.objects.get(pk=project_id)
            return project.author == request.user
        return False



from rest_framework.permissions import BasePermission
from .models import Contributor


class IsAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user


class IsContributor(BasePermission):
    def has_permission(self, request, view):
        project_id = view.kwargs.get('pk')

        if project_id:
            return Contributor.objects.filter(user=request.user, project_id=project_id).exists()

        return False
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, viewsets, serializers, status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import CustomUser, Project, Contributor, Issue, Comment
from .permissions import IsAuthorOrReadOnly, IsContributor, IsProjectAuthor
from .serializers import UserSerializer, UserListSerializer, ProjectDetailSerializer, ProjectListSerializer, \
    ContributorSerializer, IssueDetailSerializer, IssueListSerializer, CommentListSerializer, CommentDetailSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    CustomTokenObtainPairSerializer modifies the default TokenObtainPairSerializer class
    to include additional user-specific information in the token. This class is used to
    generate JWT tokens with custom claims.

    The main purpose of this class is to add the username of the authenticated user to
    the token payload. This feature is useful when custom claims need to be included in
    the JWT for various application-specific requirements.
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        return token


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom implementation of the TokenObtainPairView class.

    This class is used to customize the functionality of the TokenObtainPairView class
    by overriding its default serializer with a custom serializer. It enables extensions
    or modifications to the default behavior of the token obtain pair process, such as
    managing JWT tokens.

    :ivar serializer_class: Custom serializer that will be used to handle the token
        obtain pair process.
    :type serializer_class: type
    """
    serializer_class = CustomTokenObtainPairSerializer


class RegisterUserView(generics.CreateAPIView):
    """
    Handles user registration functionality.

    This class provides an endpoint for creating user accounts. Users are
    created using the provided serializer, which validates and saves the data.
    It uses the AllowAny permission class, meaning no authentication or
    authorization is required to access this endpoint. This class is a subclass
    of CreateAPIView, which provides a basic implementation for creating
    model instances.

    :ivar permission_classes: Specifies the permission classes applied to the
        view. In this case, the view allows unrestricted access to all users.
    :type permission_classes: list[rest_framework.permissions.AllowAny]

    :ivar queryset: Represents the set of objects available to this view.
        It uses all instances from the CustomUser model.
    :type queryset: QuerySet[CustomUser]

    :ivar serializer_class: Specifies the serializer used for validating and
        saving user data during registration.
    :type serializer_class: type[UserSerializer]
    """
    permission_classes = [AllowAny]
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer


class UserListView(generics.ListAPIView):
    """
    Represents a view for listing all users.

    This view provides an endpoint to retrieve a list of all users. Access to this
    endpoint is unrestricted as it allows any user to access the data. It leverages
    the Django Rest Framework's generic ListAPIView to simplify implementation.
    The view works with a specified query set and serializer to format the data.

    :ivar permission_classes: Permissions to access the view.
    :type permission_classes: list
    :ivar queryset: Queryset defining the set of users to be listed.
    :type queryset: QuerySet
    :ivar serializer_class: Serializer used to format the user data.
    :type serializer_class: serializers.Serializer
    """
    permission_classes = [IsAuthenticated]
    queryset = CustomUser.objects.all()
    serializer_class = UserListSerializer


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Provides functionality for retrieving, updating, or deleting a user's detail view.

    This class-based view allows interactions with the `CustomUser` model objects. It extends
    `RetrieveUpdateDestroyAPIView` to provide operations for retrieving details, updating data,
    or deleting a specific user instance. Permissions are configured to allow access to any user,
    and the view utilizes a specific serializer for representation. Query filtering in this view
    is implemented to retrieve a specific user by their primary key.

    :ivar permission_classes: List of permissions required to interact with the view.
    :type permission_classes: list
    :ivar queryset: Base queryset representing all ``CustomUser`` model instances.
    :type queryset: QuerySet
    :ivar serializer_class: Serializer class used to serialize/deserialize ``CustomUser`` objects.
    :type serializer_class: type
    """
    permission_classes = [IsAuthenticated]
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        return CustomUser.objects.filter(id=self.kwargs['pk'])


class ProjectViewSet(viewsets.ModelViewSet):
    """
    Represents a viewset for managing projects within the system.

    Provides functionality for retrieving, creating, updating, and deleting
    projects. Integrates with different serializers based on the action being
    performed. The queryset is filtered to display projects associated only
    with the currently authenticated user through their contributor role.

    :ivar permission_classes: The default permission classes used within
        the viewset. Defines access permissions for requests.
    :type permission_classes: list
    """
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly, IsContributor]

    def get_queryset(self):
        return Project.objects.filter(
            Q(contributors__user=self.request.user) | Q(author=self.request.user)
        ).distinct()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProjectDetailSerializer
        else:
            return ProjectListSerializer

    def perform_create(self, serializer):
        project = serializer.save(author=self.request.user)
        # Adds author as contributor
        Contributor.objects.create(user=self.request.user, project=project)


class ContributorViewSet(viewsets.ModelViewSet):
    """
    Provides a viewset to manage project contributors, allowing operations such as listing,
    creating, and deleting contributor objects associated with specific projects. This
    viewset is tailored to ensure that only authorized users can perform specific actions.

    Permissions and serializers are explicitly defined to integrate with Django Rest Framework.
    The viewset also incorporates project-specific filtering and validation for creating
    and deleting contributors.

    :ivar permission_classes: Defines the permission class for the viewset to allow unrestricted
        access to its endpoints.
    :type permission_classes: list
    :ivar serializer_class: Specifies the serializer class used to validate and serialize contributor
        data.
    :type serializer_class: ContributorSerializer
    """
    permission_classes = [IsProjectAuthor]
    serializer_class = ContributorSerializer

    def get_queryset(self):
        """
        Filters and returns the queryset of Contributor objects that are related to the projects
        where the currently authenticated user is listed as a contributor. This method is integral
        to ensuring that only contributors related to the authenticated user's projects are fetched.

        :return: A queryset of filtered Contributor objects.
        :rtype: QuerySet
        """
        project_id = self.kwargs.get('project_pk')
        return Contributor.objects.filter(project_id=project_id)

    def perform_create(self, serializer):
        """
        This method handles the creation of an object using the provided serializer. It ensures
        that the user creating the object is authorized to do so based on the associated project's
        author. If the requesting user is not the author of the project, a ValidationError is raised.
        Once the validation process is completed successfully, the object is saved.

        :param serializer: The serializer that contains the validated data for the object
            to be created.
        :return: None
        :raises serializers.ValidationError: If the requesting user is not the author of
            the project.
        """
        project_id = self.kwargs.get("project_pk")
        project = get_object_or_404(Project, id=project_id)

        # Check that only the author can add a contributor
        if project.author != self.request.user:
            return Response({"error": "Seul l'auteur du projet peut ajouter des contributeurs."},
                            status=status.HTTP_403_FORBIDDEN)

        # Checks if the user is already a contributor
        user = serializer.validated_data["user"]
        if Contributor.objects.filter(user=user, project=project).exists():
            raise ValidationError("Cet utilisateur est déjà contributeur du projet.")

        serializer.save(project=project)

    def destroy(self, request, *args, **kwargs):
        """
        Deletes a contributor from a specified project after validating the user permissions and
        the existence of the contributor within the project. Only the author of the project is
        authorized to perform this action. If either the project or the contributor does not exist
        or if the user is unauthorized, an appropriate error is returned.

        :param request: The HTTP request object containing the user performing the delete operation.
        :param args: Additional positional arguments passed to the method.
        :param kwargs: Additional keyword arguments passed to the method.
        :return: A Response object indicating either the success or failure of the operation.
        :rtype: Response

        :raises NotFound: If the specified project or contributor does not exist for the given project.
        :raises status.HTTP_403_FORBIDDEN: If the user is not the author of the project.
        """
        project_id = self.kwargs.get("project_pk")  # ID du projet
        contributor_id = self.kwargs.get("contributor_pk")  # ID du contributeur

        # Vérifier que le projet existe
        project = get_object_or_404(Project, id=project_id)

        # Vérifier que seul l'auteur du projet peut supprimer un contributeur
        if project.author != request.user:
            return Response({"error": "Seul l'auteur du projet peut supprimer un contributeur."},
                            status=status.HTTP_403_FORBIDDEN)

        # Vérifier que le contributeur existe pour ce projet
        contributor = Contributor.objects.filter(id=contributor_id, project_id=project_id).first()
        if not contributor:
            raise NotFound({"error": "Ce contributeur n'existe pas pour ce projet."})

        # Suppression du contributeur
        contributor.delete()
        return Response({"message": "Contributeur supprimé avec succès."}, status=status.HTTP_204_NO_CONTENT)


class IssueViewSet(viewsets.ModelViewSet):
    """
    This class represents a view set for managing issue instances in a project-based system.

    It provides API functionality for viewing, creating, and retrieving issues associated with
    specific projects. The class enforces access control policies and ensures data consistency
    through validation during operations.

    :ivar permission_classes: List of permission classes applied to the view set.
    :type permission_classes: list
    """
    permission_classes = [IsAuthorOrReadOnly]

    def get_queryset(self):
        project_id = self.kwargs.get('project_pk')
        issue_id = self.kwargs.get("issue_pk")

        if issue_id:
            return Issue.objects.filter(project_id=project_id, id=issue_id)
        return Issue.objects.filter(project_id=project_id)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return IssueDetailSerializer
        return IssueListSerializer

    def perform_create(self, serializer):
        project_id = self.kwargs.get("project_pk")
        project = get_object_or_404(Project, id=project_id)

        assigned_to = serializer.validated_data.get("assigned_to")
        if assigned_to and not Contributor.objects.filter(user=assigned_to, project=project).exists():
            raise serializers.ValidationError("L'utilisateur assigné doit être un contributeur du projet.")

        serializer.save(author=self.request.user, project=project)


class CommentViewSet(viewsets.ModelViewSet):
    """
    Handles operations related to comments using a ModelViewSet.

    This class provides CRUD operations for managing comments. It determines
    the appropriate queryset based on the authenticated user and dynamically
    assigns the serializer class depending on the action being performed.
    Also, it automatically associates the author of the comment with the
    current authenticated user during creation.

    :ivar permission_classes: Permission classes that control access to the
        viewset. Defaults to AllowAny, allowing unrestricted access.
    :type permission_classes: list
    """
    permission_classes = [IsAuthorOrReadOnly]

    def get_queryset(self):
        issue_id = self.kwargs.get('issue_pk')
        return Comment.objects.filter(issue_id=issue_id)

    def get_serializer_class(self):
        if self.action in ['retrieve', 'update', 'partial_update']:
            return CommentDetailSerializer
        return CommentListSerializer

    def perform_create(self, serializer):
        issue_id = self.kwargs.get("issue_pk")
        issue = get_object_or_404(Issue, id=issue_id)

        serializer.save(author=self.request.user, issue=issue)

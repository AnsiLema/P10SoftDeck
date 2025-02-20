from rest_framework import generics, viewsets, permissions, serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import CustomUser, Project, Contributor, Issue, Comment
from .permissions import IsContributor, IsAuthor
from .serializers import UserSerializer, UserListSerializer, ProjectDetailSerializer, ProjectListSerializer, \
ContributorSerializer, IssueDetailSerializer, IssueListSerializer, CommentListSerializer, CommentDetailSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, AuthUser


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom serializer for obtaining a token pair.

    This class extends the TokenObtainPairSerializer to include additional
    custom claims in the token payload. It modifies the token to embed
    the username of the authenticated user directly in the token, in addition
    to the standard claims provided by the base serializer.

    :ivar token: Instance containing the generated token with standard
        claims as well as additional custom claims.
    :type token: dict
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        return token


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Provides a customized view for obtaining JWT tokens.

    This class extends the `TokenObtainPairView` to utilize a custom serializer
    for generating JWT token pairs. The custom serializer can add additional
    custom logic or include extra fields in the response. Useful for scenarios
    where standard JWT generation needs to be tailored to application-specific
    requirements.

    :ivar serializer_class: The serializer class responsible for customizing
        the JWT token pair response.
    :type serializer_class: Type[TokenObtainPairSerializer]
    """
    serializer_class = CustomTokenObtainPairSerializer


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Permission class to allow read-only access for any user and write access only to the object's author.

    This class details permission settings. It permits safe HTTP methods such as GET for all users while
    restricting write actions like PUT, PATCH, and DELETE solely to the author of the object.

    :ivar SAFE_METHODS: Tuple of safe HTTP methods (e.g., GET, HEAD, OPTIONS) that are accessible to
        all users.
    :type SAFE_METHODS: tuple
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True # Allows GET
        return obj.author == request.user # Allows PUT, PATCH, DELETE to the author


class RegisterUserView(generics.CreateAPIView):
    """
    Handles the creation of a new user account.

    This class provides functionality to register a new user by creating an entry
    in the user database. It is a subclass of `generics.CreateAPIView` and
    leverages its behavior to handle POST requests for creating user records.
    It restricts access using the specified permissions and applies a serializer
    to handle data validation and user creation logic.

    :ivar permission_classes: List of permissions required to access this view.
    :type permission_classes: list
    :ivar queryset: Queryset specifying the set of records this view will act upon.
    :type queryset: QuerySet
    :ivar serializer_class: Serializer class used to validate and serialize input data.
    :type serializer_class: Serializer
    """
    permission_classes = [AllowAny]
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer


class UserListView(generics.ListAPIView):
    """
    Represents a view for listing user data.

    This class-based view provides an interface for listing user data using
    Django REST Framework. It utilizes generic ListAPIView to handle retrieval
    of user data. Access to this view is restricted to users with admin
    permissions. User data is serialized using a custom serializer.

    :ivar permission_classes: Specifies the permission classes required to
        access this view.
    :type permission_classes: list
    :ivar queryset: Defines the queryset to retrieve CustomUser objects
        from the database.
    :type queryset: QuerySet
    :ivar serializer_class: Specifies the serializer class used to serialize
        the user data.
    :type serializer_class: Serializer
    """
    permission_classes = [AllowAny]
    queryset = CustomUser.objects.all()
    serializer_class = UserListSerializer


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Handles detailed representation and manipulation of a single user's data.

    This class-based view provides functionality to retrieve, update, or delete
    a specific user instance. It ensures that only authenticated users are allowed
    to access these operations using the specified permission classes. The view uses
    the provided serializer class for data validation and transformation.

    :ivar permission_classes: List of permission classes to restrict access to
                              authenticated users only.
    :type permission_classes: list
    :ivar queryset: Base queryset used to look up user data in the database.
    :type queryset: QuerySet
    :ivar serializer_class: Serializer class used to serialize and validate user data.
    :type serializer_class: Serializer
    """
    permission_classes = [AllowAny]
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        return CustomUser.objects.filter(id=self.kwargs['pk'])


class ProjectViewSet(viewsets.ModelViewSet):
    """
    Handles CRUD operations for project views utilizing a ModelViewSet.

    This class is used to provide a complete implementation of view handling for
    the `Project` model using Django Rest Framework's `ModelViewSet`. This viewset
    enforces authentication for all endpoints. It customizes the behavior of
    queryset filtering, serializer selection, and object creation.

    :ivar permission_classes: Specifies the permission classes that are applied to
        all endpoints of this viewset. It enforces authentication for accessing
        project data.
    :type permission_classes: list
    """
    permission_classes = [AllowAny]

    def get_permissions(self):
        """Applies 'IsContributor' to see and 'IsAuthor' to create, update and delete. """
        return [AllowAny]


    def get_queryset(self):
        return Project.objects.filter(contributors__user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProjectDetailSerializer
        else:
            return ProjectListSerializer

"""
    def perform_create(self, serializer):
        # DEBUG
        
        project = serializer.save(author=self.request.user)
        Contributor.objects.create(user=self.request.user, project=project)

    def perform_destroy(self, instance):
        self.check_object_permissions(self.request, instance)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
"""

class ContributorViewSet(viewsets.ModelViewSet):
    """
    Handles operations related to contributors in a project.

    This class defines the behavior for listing, creating, retrieving, updating, and
    deleting contributors associated with projects. It requires authenticated users to
    interact with the API. Users can view contributors for projects they are associated
    with. Only the author of a project is allowed to add new contributors to that project.

    :ivar permission_classes: Defines the permission classes that ensure only
        authenticated users can access this view.
    :type permission_classes: list
    :ivar serializer_class: Determines the serializer used for handling contributor data.
    :type serializer_class: type
    """
    permission_classes = [AllowAny]
    serializer_class = ContributorSerializer

    def get_queryset(self):
        """
        Filters and returns the queryset of Contributor objects that are related to the projects
        where the currently authenticated user is listed as a contributor. This method is integral
        to ensuring that only contributors related to the authenticated user's projects are fetched.

        :return: A queryset of filtered Contributor objects.
        :rtype: QuerySet
        """
        return Contributor.objects.filter(project__contributors__user=self.request.user)

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
        project = serializer.validated_data["project"]
        if project.author != self.request.user:
            raise serializers.ValidationError("Seul l'auteur du projet peut ajouter des contributeurs.")
        serializer.save()


class IssueViewSet(viewsets.ModelViewSet):
    """
    A viewset for managing and interacting with Issue objects.

    This class provides an interface to handle CRUD operations for the Issue model.
    It restricts access to authenticated users and applies additional permissions to
    ensure only the author or individuals with read-only permissions can interact with
    the objects. The viewset also customizes serializers based on actions and validates
    assigned contributors to issues.

    :ivar permission_classes: List of permission classes applied to the viewset. It ensures
        that the user is authenticated and adheres to the IsAuthorOrReadOnly permission rules.
    :type permission_classes: list
    """
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Issue.objects.filter(project__contributors__user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return IssueDetailSerializer
        else:
            return IssueListSerializer

    def perform_create(self, serializer):
        issue = serializer.save(author=self.request.user)
        if issue.assigned_to and not Contributor.objects.filter(user=issue.assigned_to,
                                                                project=issue.project).exists():
            raise serializers.ValidationError("L'utilisateur n'est pas un contributeur du projet.")


class CommentViewSet(viewsets.ModelViewSet):
    """
    Manages CRUD operations for comments related to issues in a project management system.

    This class extends `viewsets.ModelViewSet`, allowing authenticated users to interact
    with comments they are permitted to access. It filters comments by user permissions,
    dynamically provides serializers based on the action, and ensures comments are created
    with the correct author information.

    :ivar permission_classes: List of permission classes to restrict access to authenticated
                              users only.
    :type permission_classes: list
    """
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Comment.objects.filter(issue__project__contributors__user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CommentDetailSerializer
        else:
            return CommentListSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

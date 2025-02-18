from rest_framework import generics, permissions, viewsets, permissions, serializers
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import CustomUser, Project, Contributor, Issue, Comment
from .serializers import UserSerializer, UserListSerializer, ProjectDetailSerializer, ProjectListSerializer, \
ContributorSerializer, IssueDetailSerializer, IssueListSerializer, CommentListSerializer, CommentDetailSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, AuthUser


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer for obtaining a customized token pair for authentication.

    This class extends the default TokenObtainPairSerializer to include
    additional user data in the access token payload. The purpose of this
    serializer is to customize the structure of the token and include
    specific user-related information, such as username, in the token payload.
    This enhancement allows clients consuming the token to retrieve additional
    metadata directly from the token.

    :cvar username: Adds the username of the authenticated user to the token payload.
    :type username: str
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        return token


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Class that provides custom token obtain pair functionality.

    This class is a customized version of the TokenObtainPairView from the
    REST framework's SimpleJWT package. It uses a custom serializer to
    override or extend the default behavior for token pair generation,
    which includes creating access and refresh tokens for authentication.
    Typically useful when some extra context or rules need to be applied
    while obtaining tokens in your application.

    :ivar serializer_class: Serializer used to handle the processing of token
        obtain requests.
    :type serializer_class: type
    """
    serializer_class = CustomTokenObtainPairSerializer


class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True # Allows GET
        return obj.author == request.user # Allows PUT, PATCH, DELETE to the author


class RegisterUserView(generics.CreateAPIView):
    """
    Provides a summary of actions related to user registration.

    This class-based view inherits from generics.CreateAPIView
    and is used to handle user registration. It allows public
    access to create a user instance using the provided serializer.
    The primary purpose is to expose an endpoint for creating new
    user records in the system without authentication.

    :ivar permission_classes: Specifies the permission classes
        required for the view. This is unrestricted access in this
        case, as AllowAny is used.
    :type permission_classes: List[type]
    :ivar queryset: Defines the queryset for fetching user objects.
        It queries all CustomUser instances.
    :type queryset: QuerySet
    :ivar serializer_class: Specifies the serializer used for
        creating new user instances.
    :type serializer_class: type
    """
    permission_classes = [AllowAny]
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer


class UserListView(generics.ListAPIView):
    """
    Represents a view for listing all users.

    This class-based view is used to handle HTTP GET requests and provides
    a way to retrieve a serialized list of all user objects. It exposes the
    data through a user-specified serializer and applies the defined
    permissions to access the endpoint. This view is read-only and does not
    perform create, update, or delete operations.

    :ivar permission_classes: Defines access permission classes that allow
        unrestricted access to this endpoint.
    :type permission_classes: list
    :ivar queryset: Represents the queryset of all `CustomUser` objects
        from the database.
    :type queryset: QuerySet
    :ivar serializer_class: Specifies the serializer class used to control
        the representation of the `CustomUser` objects in the response.
    :type serializer_class: type
    """
    permission_classes = [permissions.IsAdminUser]
    queryset = CustomUser.objects.all()
    serializer_class = UserListSerializer


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Provides retrieve, update, and destroy operations for a user entity.

    This view handles requests for retrieving, updating, and deleting a user
    based on their primary key (id). It uses permissions to allow unrestricted
    access. The serializer and queryset ensure proper handling of CustomUser
    objects. The `get_queryset` method allows filtering of the data to return
    a user instance matching the request parameter.

    :ivar permission_classes: A list of permissions that define the access
        level for the view.
    :type permission_classes: list
    :ivar queryset: The base queryset representing all instances of CustomUser
        objects in the database.
    :type queryset: QuerySet
    :ivar serializer_class: The serializer used to handle validation and
        transformation of CustomUser data.
    :type serializer_class: Serializer
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        return CustomUser.objects.filter(id=self.kwargs['pk'])


class ProjectViewSet(viewsets.ModelViewSet):
    """
    Provides a set of CRUD operations for Project model objects specifically
    tailored to the authenticated contributors of projects.

    This class supports retrieving, listing, creating, and updating projects.
    The `get_queryset` method ensures that the queryset is filtered based on the
    authenticated user's contributions. The serializer used depends on the
    action performed (detail view or list view).

    :ivar permission_classes: A list of permission classes enforcing that only
        authenticated users can perform operations.
    :type permission_classes: List[type]

    :ivar queryset: Filtered queryset that includes only the projects the
        authenticated user contributes to.
    :type queryset: QuerySet
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Project.objects.filter(contributors__user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProjectDetailSerializer
        else:
            return ProjectListSerializer

    def perform_create(self, serializer):
        project = serializer.save(author=self.request.user)
        Contributor.objects.create(user=self.request.user, project=project)


class ContributorViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ContributorSerializer

    def get_queryset(self):
        return Contributor.objects.filter(project__contributors__user=self.request.user)

    def perform_create(self, serializer):
        project = serializer.validated_data["project"]
        if project.author != self.request.user:
            raise serializers.ValidationError("Seul l'auteur du projet peut ajouter des contributeurs.")
        serializer.save()


class IssueViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsAuthorOrReadOnly]

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
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Comment.objects.filter(issue__project__contributors__user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CommentDetailSerializer
        else:
            return CommentListSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

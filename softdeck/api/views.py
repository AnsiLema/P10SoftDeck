from rest_framework import generics, permissions, viewsets, permissions
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import CustomUser, Project, Issue, Comment
from .serializers import UserSerializer, UserListSerializer, ProjectDetailSerializer, ProjectListSerializer, \
IssueDetailSerializer, IssueListSerializer, CommentListSerializer, CommentDetailSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, AuthUser


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        return token


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class RegisterUserView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer


class UserListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    queryset = CustomUser.objects.all()
    serializer_class = UserListSerializer


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [AllowAny]
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        return CustomUser.objects.filter(id=self.kwargs['pk'])


class ProjectListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProjectListSerializer

    def get_queryset(self):
        return Project.objects.filter(contributor__user=self.request.user)

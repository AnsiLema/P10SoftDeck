from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from .views import CustomTokenObtainPairView, RegisterUserView, UserDetailView, UserListView, ProjectViewSet, \
    ContributorViewSet, IssueViewSet, CommentViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register('projects', ProjectViewSet, basename='projects')
router.register('contributors', ContributorViewSet, basename='contributors')
router.register('issues', IssueViewSet, basename='issues')
router.register('comments', CommentViewSet, basename='comments')


urlpatterns = [
    # Authentication
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterUserView.as_view(), name='register'),

    # User management
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('', include(router.urls)),
]
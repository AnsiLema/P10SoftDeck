from django.urls import path, include
from .views import CustomTokenObtainPairView, RegisterUserView, UserDetailView, UserListView, ProjectViewSet, \
    ContributorViewSet, IssueViewSet, CommentViewSet
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register('projects', ProjectViewSet, basename='projects')
router.register('contributors', ContributorViewSet, basename='contributors')
router.register('issues', IssueViewSet, basename='issues')
router.register('comments', CommentViewSet, basename='comments')


urlpatterns = [
    # Authentication
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('register/', RegisterUserView.as_view(), name='register'),

    # User management
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('', include(router.urls)),

    # Contributors
    path('projects/<int:project_pk>/contributors/', ContributorViewSet.as_view(
        {'post': 'create', 'get': 'list'}), name='project-contributors'),
    path('projects/<int:project_pk>/contributors/<int:contributor_pk>/', ContributorViewSet.as_view(
        {'delete': 'destroy'}), name='project-contributor-delete'),

    # Issues
    path('projects/<int:project_pk>/issues/', IssueViewSet.as_view({'post': 'create', 'get': "list"}),
         name='project-issues'),
    path('projects/<int:project_pk>/issues/<int:issue_pk>/', IssueViewSet.as_view(
        {'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'}), name='project-issue-detail'),

    # Comments
    path('projects/<int:project_pk>/issues/<int:issue_pk>/comments/',
         CommentViewSet.as_view({'post': 'create', 'get': 'list'}), name='issue-comments'),
    path('projects/<int:project_pk>/issues/<int:issue_pk>/comments/<uuid:pk>/',
         CommentViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'}),
         name='issue-comment-detail'),
]

# urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PostViewSet, 
    ConnectionViewSet, 
    GroupMemberViewSet, 
    PostReactionViewSet, 
    FileUploadViewSet, 
    UserCreate, 
    PasswordResetRequestView, 
    PasswordResetView, 
    UserDetailView,
    LoginView,  # Add this import
)

router = DefaultRouter()
router.register(r'posts', PostViewSet)
router.register(r'connections', ConnectionViewSet)
router.register(r'group-members', GroupMemberViewSet)
router.register(r'post-reactions', PostReactionViewSet)
router.register(r'file-uploads', FileUploadViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/signup/', UserCreate.as_view(), name='user-create'),
    path('auth/login/', LoginView.as_view(), name='login'),  # Add this line
    path('auth/request-reset/', PasswordResetRequestView.as_view(), name='request-reset'),
    path('auth/reset-password/', PasswordResetView.as_view(), name='reset-password'),
    path('user/<str:username>/', UserDetailView.as_view(), name='user-detail'),
]

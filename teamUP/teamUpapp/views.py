from rest_framework import viewsets
from rest_framework import generics
from .models import Post, Connection, GroupMember, PostReaction, FileUpload
from .serializers import PostSerializer, ConnectionSerializer, GroupMemberSerializer, PostReactionSerializer, FileUploadSerializer, UserSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from .models import Group, GroupMember
from .serializers import UserSerializer, GroupSerializer
from rest_framework.generics import RetrieveAPIView
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .models import Post, Group
from .serializers import PostSerializer
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

class PostDetailView(RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]  # Only allow authenticated users

    def get_object(self):
        post_id = self.kwargs.get('id')
        return get_object_or_404(Post, id=post_id)
    

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        username = request.data.get('user')
        group_name = request.data.get('recipient_group', None)

        if not username:
            return Response({'error': 'User is required'}, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(User, username=username)
        request.data['user'] = user.id

        if group_name:
            group = get_object_or_404(Group, name=group_name)
            request.data['recipient_group'] = group.id
        else:
            request.data['recipient_group'] = None

        return super().create(request, *args, **kwargs)
    
class PostsByParentIDView(generics.ListAPIView):
    serializer_class = PostSerializer

    def get(self, request, *args, **kwargs):
        parent_id = self.kwargs.get('postID')
        print(parent_id)
        if not parent_id:
            return Response({"error": "postID parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        posts = Post.objects.filter(parent_id=parent_id)
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)
    


class ConnectionViewSet(viewsets.ModelViewSet):
    queryset = Connection.objects.all()
    serializer_class = ConnectionSerializer
    permission_classes = [IsAuthenticated]

class GroupMemberViewSet(viewsets.ModelViewSet):
    queryset = GroupMember.objects.all()
    serializer_class = GroupMemberSerializer
    permission_classes = [IsAuthenticated]


class PostReactionViewSet(viewsets.ModelViewSet):
    queryset = PostReaction.objects.all()
    serializer_class = PostReactionSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Get the user and post from the request data
        user = request.user
        post_id = request.data.get('post')
        post = get_object_or_404(Post, id=post_id)
        
        # Ensure that a PostReaction can be created
        reaction = PostReaction.objects.create(reactor=user, post=post, name=request.data.get('name'))
        serializer = self.get_serializer(reaction)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        # Ensure the user is the owner of the reaction
        reaction = self.get_object()
        if reaction.reactor != request.user:
            return Response({'error': 'You are not authorized to delete this reaction.'}, status=status.HTTP_403_FORBIDDEN)

        # Proceed to delete the reaction
        return super().destroy(request, *args, **kwargs)
    
class FileUploadViewSet(viewsets.ModelViewSet):
    queryset = FileUpload.objects.all()
    serializer_class = FileUploadSerializer
    permission_classes = [IsAuthenticated]

class UserDetailView(RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'username'

    def get(self, request, *args, **kwargs):
        username = self.kwargs.get('username')
        user = get_object_or_404(User, username=username)
        serializer = self.get_serializer(user)
        # print(f'Serializer data: {serializer.data}')
        return Response(serializer.data)


class UserCreate(APIView):
    def post(self, request, format='json'):
        # Print the request data including the password
        username = request.data.get('username')
        password = request.data.get('password')
        # print(f"Received request with username: {username} and password: {password}")

        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                # Generate token
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                response_data = {
                    'username': user.username,
                    'access_token': access_token,
                }
                return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        username = request.data.get('username')
        password = request.data.get('password')
        # print(f"Attempting to authenticate with username: {username} and password: {password}")

        user = authenticate(request, username=username, password=password)
        # print(f"Result of authentication: {user}")

        if user is not None:
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            response_data = {
                'username': user.username,
                'access_token': access_token,
                'refresh_token': str(refresh),
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class UserGroupsView(APIView):
    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        group_memberships = GroupMember.objects.filter(user=user)
        groups = [membership.group for membership in group_memberships]
        serializer = GroupSerializer(groups, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class GroupMembersView(APIView):
    def get(self, request, group_name):
        group = get_object_or_404(Group, name=group_name)
        members = GroupMember.objects.filter(group=group)
        users = [member.user for member in members]
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class PasswordResetRequestView(APIView):
    def post(self, request):
        # Implement logic for password reset request
        return Response({"message": "Password reset link sent."}, status=status.HTTP_200_OK)

class PasswordResetView(APIView):
    def post(self, request):
        # Implement logic for password reset
        return Response({"message": "Password reset successful."}, status=status.HTTP_200_OK)


# class PostViewSet(viewsets.ModelViewSet):
#     queryset = Post.objects.all()
#     serializer_class = PostSerializer
#     permission_classes = [IsAuthenticated]

#     # def create(self, request, *args, **kwargs):
#     #     username = request.data.get('user')
#     #     group_name = request.data.get('recipient_group')
#     #     user = get_object_or_404(User, username=username)
#     #     group = get_object_or_404(Group, name=group_name)
#     #     request.data['user'] = user.id
#     #     request.data['recipient_group'] = group.id
#     #     return super().create(request, *args, **kwargs)

#     def create(self, request, *args, **kwargs):
#         username = request.data.get('user')
#         group_name = request.data.get('recipient_group', None)
#         user = get_object_or_404(User, username=username)
#         request.data['user'] = user.id
#         if group_name:
#             group = get_object_or_404(Group, name=group_name)
#             request.data['recipient_group'] = group.id
#         else:
#             request.data['recipient_group'] = None

#         return super().create(request, *args, **kwargs)
        
#     def get_queryset(self):
#         queryset = Post.objects.all()
#         group_name = self.request.query_params.get('recipient_group', None)
#         if group_name:
#             group = get_object_or_404(Group, name=group_name)
#             queryset = queryset.filter(recipient_group=group)
#         return queryset
    
# class PostReactionViewSet(viewsets.ModelViewSet):
#     queryset = PostReaction.objects.all()
#     serializer_class = PostReactionSerializer
#     permission_classes = [IsAuthenticated]

#     def create(self, request, *args, **kwargs):
#         # Get the user and post from the request data
#         user = request.user
#         post_id = request.data.get('post')
#         reaction_name = request.data.get('name')

#         # Ensure post exists
#         post = get_object_or_404(Post, id=post_id)

#         # Check if the user already reacted to this post with the same reaction
#         existing_reaction = PostReaction.objects.filter(reactor=user, post=post, name=reaction_name).first()
#         if existing_reaction:
#             return Response({'error': 'You have already reacted to this post with this reaction.'}, status=status.HTTP_400_BAD_REQUEST)

#         # Create the reaction
#         post_reaction = PostReaction.objects.create(
#             reactor=user,
#             post=post,
#             name=reaction_name
#         )
#         serializer = self.get_serializer(post_reaction)
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
    
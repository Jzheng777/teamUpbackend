from rest_framework import viewsets
from rest_framework import generics
from .serializers import PostSerializer, ConnectionSerializer, GroupMemberSerializer, PostReactionSerializer, FileUploadSerializer, UserSerializer, GroupSerializer, UserProfileSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from .models import Group, GroupMember, UserProfile, Post, Group, User, Connection, PostReaction, FileUpload
from rest_framework.generics import RetrieveAPIView
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from rest_framework.decorators import action

class PostDetailView(RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

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
    
    def partial_update(self, request, *args, **kwargs):
        post_instance = self.get_object()
        username = request.data.get('user', None)
        if username:
            user = get_object_or_404(User, username=username)
            request.data['user'] = user.id
        group_name = request.data.get('recipient_group', None)
        if group_name:
            group = get_object_or_404(Group, name=group_name)
            request.data['recipient_group'] = group.id
        elif 'recipient_group' in request.data:
            request.data['recipient_group'] = None
        return super().partial_update(request, *args, **kwargs)
    
class PostsByParentIDView(generics.ListAPIView):
    serializer_class = PostSerializer

    def get(self, request, *args, **kwargs):
        parent_id = self.kwargs.get('postID')
        if not parent_id:
            return Response({"error": "postID parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
        posts = Post.objects.filter(parent_id=parent_id)
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)

class UpdateConnectionAttributesView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, connection_id):
        # Get the connection instance by ID
        connection = get_object_or_404(Connection, id=connection_id)
        
        # Get the 'attributes' field from the request data
        attributes = request.data.get('attributes', None)
        if attributes is None:
            return Response({"error": "Attributes field is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update the connection's attributes
        connection.attributes.update(attributes)
        connection.save()

        # Serialize and return the updated connection
        serializer = ConnectionSerializer(connection)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ConnectionViewSet(viewsets.ModelViewSet):
    queryset = Connection.objects.all()
    serializer_class = ConnectionSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        to_user_username = request.data.get('toUserID')
        from_user_username = request.data.get('fromUserID')
        if not to_user_username or not from_user_username:
            return Response({'error': 'Both toUserID and fromUserID are required'}, status=status.HTTP_400_BAD_REQUEST)
        to_user = get_object_or_404(User, username=to_user_username)
        from_user = get_object_or_404(User, username=from_user_username)
        data = {
            'to_user': to_user.id,
            'from_user': from_user.id,
            'attributes': request.data.get('attributes', {})
        }
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get_queryset(self):
        queryset = super().get_queryset()
        to_user = self.request.query_params.get('to_user', None)
        from_user = self.request.query_params.get('from_user', None)
        if to_user:
            queryset = queryset.filter(to_user__username=to_user)
        if from_user:
            queryset = queryset.filter(from_user__username=from_user)

        return queryset

    @action(detail=False, methods=['get'])
    def connections(self, request):
        to_user = request.query_params.get('to_user')
        from_user = request.query_params.get('from_user')
        if not to_user and not from_user:
            return Response({'error': 'Please provide at least to_user or from_user'}, status=status.HTTP_400_BAD_REQUEST)
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GroupMemberViewSet(viewsets.ModelViewSet):
    queryset = GroupMember.objects.all()
    serializer_class = GroupMemberSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        username = request.data.get('username')
        group_name = request.data.get('group')
        if not username or not group_name:
            return Response({'error': 'Username and group name are required'}, status=status.HTTP_400_BAD_REQUEST)
        user = get_object_or_404(User, username=username)
        group = get_object_or_404(Group, name=group_name)
        GroupMember.objects.create(user=user, group=group)
        return Response({'message': f'User {user.username} added to group {group.name}'}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['delete'])
    def delete_by_username_and_group(self, request):
        username = request.data.get('username')
        group_name = request.data.get('group')
        if not username or not group_name:
            return Response({'error': 'Username and group name are required'}, status=status.HTTP_400_BAD_REQUEST)
        user = get_object_or_404(User, username=username)
        group = get_object_or_404(Group, name=group_name)
        try:
            group_member = GroupMember.objects.get(user=user, group=group)
        except GroupMember.DoesNotExist:
            return Response({'error': 'GroupMember not found'}, status=status.HTTP_404_NOT_FOUND)
        group_member.delete()
        return Response({'message': f'User {user.username} removed from group {group.name}'}, status=status.HTTP_204_NO_CONTENT)

class UserListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

class PostReactionViewSet(viewsets.ModelViewSet):
    queryset = PostReaction.objects.all()
    serializer_class = PostReactionSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user
        post_id = request.data.get('post')
        post = get_object_or_404(Post, id=post_id)
        reaction = PostReaction.objects.create(reactor=user, post=post, name=request.data.get('name'))
        serializer = self.get_serializer(reaction)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        reaction = self.get_object()
        if reaction.reactor != request.user:
            return Response({'error': 'You are not authorized to delete this reaction.'}, status=status.HTTP_403_FORBIDDEN)
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
        return Response(serializer.data)

class UserProfileUpdateView(generics.UpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'username'

    def get_object(self):
        username = self.kwargs.get('username')
        user = get_object_or_404(User, username=username)
        profile, created = UserProfile.objects.get_or_create(user=user)
        return profile

    def patch(self, request, *args, **kwargs):
        partial = True
        serializer = self.get_serializer(self.get_object(), data=request.data, partial=partial)
        if not serializer.is_valid():
            print(f"Serializer Errors: {serializer.errors}")
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserCreate(APIView):
    def post(self, request, format='json'):
        username = request.data.get('username')
        password = request.data.get('password')
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
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

        user = authenticate(request, username=username, password=password)
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
        return Response({"message": "Password reset link sent."}, status=status.HTTP_200_OK)

class PasswordResetView(APIView):
    def post(self, request):
        return Response({"message": "Password reset successful."}, status=status.HTTP_200_OK)
    
from rest_framework import serializers
from .models import Post, Connection, GroupMember, PostReaction, FileUpload, UserProfile
from django.contrib.auth.models import User

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'

class ConnectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Connection
        fields = '__all__'

class GroupMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupMember
        fields = '__all__'

class PostReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostReaction
        fields = '__all__'

class FileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileUpload
        fields = '__all__'

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['search_history', 'make_private', 'allow_follow', 'show_ranking', 'picture']


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(required=True, allow_null=True)
    posts = PostSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'profile', 'posts']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        profile_data = validated_data.pop('profile', None)
        password = validated_data.pop('password', None)  # Extract the password

        user = User(**validated_data)  # Create the user without saving it yet
        if password:
            user.set_password(password)  # Hash the password
        user.save()  # Save the user to the database

        if profile_data is None:
            UserProfile.objects.get_or_create(user=user)
        else:
            UserProfile.objects.update_or_create(user=user, defaults=profile_data)
        
        return user

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        profile, created = UserProfile.objects.get_or_create(user=instance)
        representation['profile'] = UserProfileSerializer(profile).data
        return representation


# class UserSerializer(serializers.ModelSerializer):
#     profile = UserProfileSerializer(required=True, allow_null=True)
#     posts = PostSerializer(many=True, read_only=True)

#     class Meta:
#         model = User
#         fields = ['username', 'email', 'profile', 'posts']
#         extra_kwargs = {'password': {'write_only': True}}

#     def create(self, validated_data):
#         profile_data = validated_data.pop('profile', None)
#         user = User.objects.create_user(**validated_data)
        
#         if profile_data is None:
#             UserProfile.objects.get_or_create(user=user)
#         else:
#             UserProfile.objects.update_or_create(user=user, defaults=profile_data)
        
#         return user

#     def to_representation(self, instance):
#         representation = super().to_representation(instance)
#         profile, created = UserProfile.objects.get_or_create(user=instance)
#         representation['profile'] = UserProfileSerializer(profile).data
#         return representation

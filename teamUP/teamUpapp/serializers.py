from rest_framework import serializers
from .models import Post, Connection, GroupMember, PostReaction, FileUpload, UserProfile, Group
from django.contrib.auth.models import User

class PostReactionSerializer(serializers.ModelSerializer):
    post_username = serializers.SerializerMethodField()
    reactor_username = serializers.SerializerMethodField()

    class Meta:
        model = PostReaction
        fields = ['id', 'reactor', 'post', 'name', 'post_username', 'reactor_username']

    def get_post_username(self, obj):
        return obj.post.user.username

    def get_reactor_username(self, obj):
        return obj.reactor.username

        
class PostSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True)
    username = serializers.SerializerMethodField()
    reactions = PostReactionSerializer(source='postreaction_set', many=True, read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'content', 'user', 'username', 'reactions', 'recipient_group', 'parent', 'attributes', 'created_at']

    def get_username(self, obj):
        return obj.user.username
    
    def get_created_at(self, obj):
        return obj.created_at.strftime('%m/%d/%Y')


class ConnectionSerializer(serializers.ModelSerializer):
    to_user_username = serializers.SerializerMethodField()
    from_user_username = serializers.SerializerMethodField()
    to_user_profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = Connection
        fields = ['id', 'to_user', 'from_user', 'attributes', 'to_user_username', 'from_user_username', 'to_user_profile_picture']

    def get_to_user_username(self, obj):
        return obj.to_user.username

    def get_from_user_username(self, obj):
        return obj.from_user.username

    def get_to_user_profile_picture(self, obj):
        # Fetch the profile picture from the UserProfile model
        return obj.to_user.userprofile.picture if hasattr(obj.to_user, 'userprofile') else None



class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['name']

class GroupMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupMember
        fields = '__all__'

class FileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileUpload
        fields = '__all__'
    
    def validate_file(self, value):
        if not value.name.endswith(('.png', '.jpg', '.jpeg', '.gif', '.pdf')):
            raise serializers.ValidationError("Unsupported file type.")
        return value
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        file_url = representation['file']
        if file_url.startswith('/media/'):
            representation['file'] = '/api' + file_url
        return representation

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['search_history', 'make_private', 'allow_follow', 'show_ranking', 'picture', 'exp', 'find', 'description', 'discord', 'ranks', 'profanity_filter']
        extra_kwargs = {
            'search_history': {'required': False},
            'make_private': {'required': False},
            'allow_follow': {'required': False},
            'show_ranking': {'required': False},
            'picture': {'required': False},
            'exp': {'required': False},
            'find': {'required': False},
            'description': {'required': False},
            'discord': {'required': False},
            'ranks': {'required': False},
        }



class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(required=True, allow_null=True)
    posts = PostSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'profile', 'posts']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        profile_data = validated_data.pop('profile', None)
        password = validated_data.pop('password', None)

        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
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
    
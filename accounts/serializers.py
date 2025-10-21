from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from .models import CustomUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class UserSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)
    full_name = serializers.CharField(write_only=True)
    profile_picture = serializers.ImageField(required=False, allow_null=True)
    birthday = serializers.DateField(required=False, allow_null=True)
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'full_name', 'password', 
                 'confirm_password', 'profile_picture', 'birthday']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_username(self, value):
        if CustomUser.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    def validate_email(self, value):
        if CustomUser.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value

    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def validate(self, data):
        if data.get('password') != data.get('confirm_password'):
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        
        # full_name splitting
        full_name = validated_data.pop('full_name')
        names = full_name.strip().split(' ', 1)
        first_name = names[0]
        last_name = names[1] if len(names) > 1 else ''
        
        # Extract profile_picture 
        profile_picture = validated_data.pop('profile_picture', None)
        birthday = validated_data.pop('birthday', None)
        
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=first_name,
            last_name=last_name,
            birthday=birthday 
        )
        
        # Set profile picture 
        if profile_picture:
            user.profile_picture = profile_picture
            user.save()
        
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    profile_picture_url = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'first_name', 'last_name', 'email', 'username', 
                 'profile_picture', 'profile_picture_url', 'full_name']
        read_only_fields = ['id', 'username', 'email']

    def get_profile_picture_url(self, obj):
        """Return full URL for profile picture"""
        request = self.context.get('request')
        if obj.profile_picture:
            if request:
                return request.build_absolute_uri(obj.profile_picture.url)
            return obj.profile_picture.url
        return None

    def get_full_name(self, obj):
        """Return formatted full name"""
        return f"{obj.first_name} {obj.last_name}".strip()

    def update(self, instance, validated_data):
        """Handle profile updates including profile picture"""
        # Update basic fields
        for attr, value in validated_data.items():
            if attr != 'profile_picture':
                setattr(instance, attr, value)
        
        # Handle profile picture separately
        if 'profile_picture' in validated_data:
            profile_picture = validated_data['profile_picture']
            if profile_picture:
                # Delete old profile picture if exists and not default
                if (instance.profile_picture and 
                    instance.profile_picture.name != 'profile_pics/default.jpg'):
                    try:
                        instance.profile_picture.delete(save=False)
                    except:
                        pass  # Ignore if file doesn't exist
                
                instance.profile_picture = profile_picture
            elif profile_picture is None:
                # User wants to remove profile picture
                if (instance.profile_picture and 
                    instance.profile_picture.name != 'profile_pics/default.jpg'):
                    try:
                        instance.profile_picture.delete(save=False)
                    except:
                        pass
                instance.profile_picture = 'profile_pics/default.jpg'
        
        instance.save()
        return instance

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT serializer that allows login with either email or username."""
    
    def validate(self, attrs):
        username_or_email = attrs.get("username") or attrs.get("email")
        password = attrs.get("password")
        
        user = None
        if "@" in username_or_email:  # login with email
            try:
                user_obj = CustomUser.objects.get(email=username_or_email)
                user = authenticate(username=user_obj.username, password=password)
            except CustomUser.DoesNotExist:
                user = None
        else:  # login with username
            user = authenticate(username=username_or_email, password=password)
        
        if not user:
            raise serializers.ValidationError("Invalid credentials")
        
        attrs["username"] = user.username  # force username for JWT
        return super().validate(attrs)
    
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'birthday', 'profile_picture']  # include yours

    def validate_username(self, value):
        # ADDED: check for duplicate usernames
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    def validate_email(self, value):
        # ADDED: check for duplicate emails
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value
from rest_framework import serializers
from apps.users.models import CustomUser, Profile
from django.contrib.auth.password_validation import validate_password
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom serializer to add additional claims in the JWT token.
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['email'] = user.email
        token['role'] = user.role
        return token
# User Serializer
class UserSerializer(serializers.ModelSerializer):
    """
    Serializer to display user details.
    """
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'is_active', 'first_name', 'last_name')
# Profile Serializer
class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer to handle user profile updates, including pending email changes.
    """
    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = (
            'user', 'address', 'city', 'country', 'date_of_birth',
            'profile_picture', 'phone_number'
        )

    def update(self, instance, validated_data):
        """
        Update profile and handle email change if necessary.
        """
        user_data = validated_data.pop('user', {})
        user = instance.user

        # Update user fields
        for field, value in user_data.items():
            setattr(user, field, value)
        user.save()

        # Update profile fields
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()

        return instance
        
    
class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for registering a new user with email verification.
    """
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password', 'password2', 'first_name', 'last_name')

    def validate(self, attrs):
        """
        Validate that the two provided passwords match.
        """
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        """
        Create a new user with email verification and inactive status.
        """
        email = validated_data.pop('email')
        validated_data.pop('password2')

        # Create user with pending email for verification
        user = CustomUser.objects.create_user(
            email=email,
            **validated_data
        )
        user.is_active = True
        user.save()

        # Create profile
        Profile.objects.create(user=user)
        return user


# User Login Serializer
class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    """
    username = serializers.CharField()
    password = serializers.CharField()

class UserLogoutSerializer(serializers.Serializer):
    """
    Serializer for user logout.
    """
    pass
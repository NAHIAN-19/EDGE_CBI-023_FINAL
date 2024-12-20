from apps.users.models import CustomUser, Profile
from apps.users.serializers import UserSerializer, ProfileSerializer, UserRegistrationSerializer, UserLoginSerializer, UserLogoutSerializer, MyTokenObtainPairSerializer
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from django.contrib.auth import authenticate, login, logout
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import serializers

class MyTokenObtainPairView(TokenObtainPairView):
    """Custom token view that uses MyTokenObtainPairSerializer"""
    serializer_class = MyTokenObtainPairSerializer
    
class UserRegistrationView(CreateAPIView):
    """
    Handles user registration and sends verification OTP.
    """
    serializer_class = UserRegistrationSerializer
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        username = request.data.get('username')
        email = request.data.get('email')

        # Check for an existing user with pending verification
        existing_user = CustomUser.objects.filter(
            username=username,
            email=email,
        ).first()

        # Create a new user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()


        return Response({
            "message": "Registration successful.",
        }, status=status.HTTP_201_CREATED)

class UserLoginView(APIView):
    """
    Handles user login and returns JWT tokens.
    """
    permission_classes = (AllowAny,)
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password']
        )
        
        if user is None:
            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
            

        refresh = RefreshToken.for_user(user)
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'username': user.username,
            'email': user.email,
        })

class LogoutView(APIView):
    """
    Handles user logout by blacklisting the refresh token.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserLogoutSerializer
    def post(self, request):
        try:
            # Get the refresh token from the request data
            refresh_token = request.data["refresh"]
            # Instantiate a RefreshToken object with the refresh token
            token = RefreshToken(refresh_token)
            # Add the token to the blacklist
            token.blacklist()
            return Response({"message": "Logged out successfully"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
        
class ProfileView(RetrieveUpdateAPIView):
    """
    Handles user profile retrieval and updates.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer

    def get_object(self):
        """
        Return the profile of the authenticated user or a user by their ID.
        If user_id is provided in the URL, return that user's profile,
        otherwise, return the current user's profile.
        """
        user_id = self.kwargs.get('user_id')
        if user_id:
            try:
                return Profile.objects.get(user__id=user_id)
            except Profile.DoesNotExist:
                raise serializers.ValidationError(
                    {"error": f"Profile not found for user ID {user_id}"}
                )
        return self.request.user.profile

    def update(self, request, *args, **kwargs):
        """
        Handle profile updates, including triggering OTPs for email change.
        """
        user_id = kwargs.get('user_id')
        if user_id and user_id != str(request.user.id):
            return Response(
                {"error": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN
            )
        instance = request.user.profile
        partial = kwargs.pop('partial', True)  # Allow partial updates
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            response_data = {
                "message": "Profile updated successfully",
                "profile": serializer.data,
            }

            return Response(response_data)

        except serializers.ValidationError as e:
            return Response({"error": e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": "An unexpected error occurred while updating your profile. Please try again."},
                status=status.HTTP_400_BAD_REQUEST
            )

    def perform_update(self, serializer):
        """
        Perform the actual update of the profile instance.
        """
        serializer.save()
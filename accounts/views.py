from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import UserProfileSerializer, UserSerializer, MyTokenObtainPairSerializer
from .models import CustomUser
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
import logging
from django.db import IntegrityError

logger = logging.getLogger(__name__)

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser])
def register_user(request):
    logger.info(f"Registration attempt with data keys: {list(request.data.keys())}")
    
    serializer = UserSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            user = serializer.save()
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            
            # Get profile picture URL
            profile_picture_url = None
            if user.profile_picture:
                profile_picture_url = request.build_absolute_uri(user.profile_picture.url)
            
            response_data = {
                'message': 'User registered successfully.',
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'full_name': f"{user.first_name} {user.last_name}".strip(),
                    'birthday': user.birthday,
                    'profile_picture': profile_picture_url
                }
            }
            
            logger.info(f"User {user.username} registered successfully")
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except IntegrityError as e:
            logger.error(f"Database integrity error during registration: {str(e)}")
            
            # Provide specific error messages
            error_msg = str(e).lower()
            if 'username' in error_msg:
                return Response(
                    {'error': 'This username is already taken.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            elif 'email' in error_msg:
                return Response(
                    {'error': 'This email is already registered.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                return Response(
                    {'error': 'Registration failed. Please try again.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        except Exception as e:
            logger.error(f"Unexpected error during registration: {str(e)}")
            return Response(
                {'error': 'Registration failed. Please try again.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    # Validation errors
    logger.error(f"Registration validation failed: {serializer.errors}")
    return Response(
        {'error': 'Invalid data.', 'details': serializer.errors},
        status=status.HTTP_400_BAD_REQUEST
    )

@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def profile_view(request):
    user = request.user
    
    if request.method == 'GET':
        serializer = UserProfileSerializer(user, context={'request': request})
        return Response(serializer.data)
    
    elif request.method in ['PUT', 'PATCH']:
        logger.info(f"Profile update for {user.username} with data: {list(request.data.keys())}")
        
        # Handle file upload specifically
        partial = request.method == 'PATCH'
        serializer = UserProfileSerializer(
            user, 
            data=request.data, 
            partial=partial,
            context={'request': request}
        )
        
        if serializer.is_valid():
            updated_user = serializer.save()
            
            logger.info(f"Profile updated successfully for {user.username}")
            
            return Response({
                'message': 'Profile updated successfully.',
                'user': UserProfileSerializer(updated_user, context={'request': request}).data
            })
        
        logger.error(f"Profile update failed for {user.username}: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        refresh_token = request.data.get("refresh_token")
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
    except Exception as e:
        logger.warning(f"Token blacklist failed: {e}")
    
    return Response({"message": "Logged out successfully"})

# Additional utility view for profile picture upload
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_profile_picture(request):
    """Dedicated endpoint for profile picture uploads"""
    user = request.user
    
    if 'profile_picture' not in request.FILES:
        return Response({
            'error': 'No profile picture provided'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    profile_picture = request.FILES['profile_picture']
    
    # Validate file type
    allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if profile_picture.content_type not in allowed_types:
        return Response({
            'error': 'Invalid file type. Please upload a JPEG, PNG, GIF, or WebP image.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate file size (5MB limit)
    if profile_picture.size > 5 * 1024 * 1024:
        return Response({
            'error': 'File too large. Please upload an image smaller than 5MB.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Delete old profile picture if exists and not default
    if (user.profile_picture and 
        user.profile_picture.name != 'profile_pics/default.jpg'):
        try:
            user.profile_picture.delete(save=False)
        except:
            pass  # Ignore if file doesn't exist
    
    # Save new profile picture
    user.profile_picture = profile_picture
    user.save()
    
    profile_picture_url = request.build_absolute_uri(user.profile_picture.url)
    
    logger.info(f"Profile picture updated for {user.username}")
    
    return Response({
        'message': 'Profile picture updated successfully.',
        'profile_picture_url': profile_picture_url
    })

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_profile_picture(request):
    """Remove user's profile picture and set to default"""
    user = request.user
    
    # Delete current profile picture if not default
    if (user.profile_picture and 
        user.profile_picture.name != 'profile_pics/default.jpg'):
        try:
            user.profile_picture.delete(save=False)
        except:
            pass
    
    # Set to default
    user.profile_picture = 'profile_pics/default.jpg'
    user.save()
    
    logger.info(f"Profile picture removed for {user.username}")
    
    return Response({
        'message': 'Profile picture removed successfully.',
        'profile_picture_url': request.build_absolute_uri(user.profile_picture.url)
    })
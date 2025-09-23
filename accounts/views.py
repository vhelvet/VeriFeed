from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import UserProfileSerializer, UserSerializer
from .models import CustomUser

@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser])
def register_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        # Create token for immediate login after registration
        token, created = Token.objects.get_or_create(user=user)
        return Response(
            {
                'message': 'User registered successfully.',
                'token': token.key,
                'user': {
                    'username': user.username,
                    'email': user.email,
                    'full_name': f"{user.first_name} {user.last_name}".strip(),
                    'profile_picture': user.profile_picture.url if user.profile_picture else None
                }
            },
            status=status.HTTP_201_CREATED
        )
    return Response(
        {'error': 'Invalid data.', 'details': serializer.errors},
        status=status.HTTP_400_BAD_REQUEST
    )

@api_view(['POST'])
@permission_classes([AllowAny])
def user_login(request):
    username_or_email = request.data.get('username')
    password = request.data.get('password')

    if not username_or_email or not password:
        return Response(
            {'error': 'Username/email and password are required.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = None
    if '@' in username_or_email:
        try:
            user_obj = CustomUser.objects.get(email=username_or_email)
            user = authenticate(username=user_obj.username, password=password)
        except CustomUser.DoesNotExist:
            user = None
    else:
        user = authenticate(username=username_or_email, password=password)

    if user:
        token, created = Token.objects.get_or_create(user=user)
        return Response(
            {
                'token': token.key,
                'message': 'Login successful.',
                'user': {
                    'username': user.username,
                    'email': user.email,
                    'full_name': f"{user.first_name} {user.last_name}".strip(),
                    'profile_picture': user.profile_picture.url if user.profile_picture else None
                }
            },
            status=status.HTTP_200_OK
        )
    else:
        return Response(
            {'error': 'Invalid credentials.'},
            status=status.HTTP_401_UNAUTHORIZED
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_logout(request):
    try:
        if hasattr(request.user, 'auth_token'):
            request.user.auth_token.delete()
            return Response(
                {'message': 'Successfully logged out.'},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {'error': 'No token found for this user.'},
                status=status.HTTP_400_BAD_REQUEST
            )
    except Exception as e:
        return Response(
            {'error': 'An error occurred during logout.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def user_profile(request):
    user = request.user

    if request.method == 'GET':
        serializer = UserProfileSerializer(user)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = UserProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Profile updated successfully.',
                'data': serializer.data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
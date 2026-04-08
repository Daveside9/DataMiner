from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import login, logout
from django.utils import timezone
from .models import User, UserProfile
from .serializers import (
    UserRegistrationSerializer, 
    UserLoginSerializer, 
    UserSerializer, 
    UserProfileSerializer,
    PasswordChangeSerializer
)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_user(request):
    """Register a new user"""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'success': True,
            'message': 'Account created successfully! Welcome to BetVision Pro!',
            'user': UserSerializer(user).data,
            'token': token.key
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_user(request):
    """Login user"""
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        
        # Update last active
        user.update_last_active()
        
        return Response({
            'success': True,
            'message': f'Welcome back, {user.full_name}!',
            'user': UserSerializer(user).data,
            'token': token.key
        }, status=status.HTTP_200_OK)
    
    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_user(request):
    """Logout user"""
    try:
        # Delete the user's token
        request.user.auth_token.delete()
        return Response({
            'success': True,
            'message': 'Logged out successfully'
        }, status=status.HTTP_200_OK)
    except:
        return Response({
            'success': False,
            'message': 'Error logging out'
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_user_profile(request):
    """Get current user profile"""
    user = request.user
    user.update_last_active()
    
    return Response({
        'success': True,
        'user': UserSerializer(user).data
    }, status=status.HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def update_user_profile(request):
    """Update user profile"""
    user = request.user
    serializer = UserSerializer(user, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        return Response({
            'success': True,
            'message': 'Profile updated successfully',
            'user': serializer.data
        }, status=status.HTTP_200_OK)
    
    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def change_password(request):
    """Change user password"""
    serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        # Delete old token and create new one
        user.auth_token.delete()
        token = Token.objects.create(user=user)
        
        return Response({
            'success': True,
            'message': 'Password changed successfully',
            'token': token.key
        }, status=status.HTTP_200_OK)
    
    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_user_stats(request):
    """Get user usage statistics"""
    user = request.user
    
    # Calculate additional stats
    active_sessions = user.monitoring_sessions.filter(status='active').count()
    completed_sessions = user.monitoring_sessions.filter(status='completed').count()
    total_changes = user.monitoring_sessions.aggregate(
        total=models.Sum('changes_detected')
    )['total'] or 0
    
    return Response({
        'success': True,
        'stats': {
            'subscription_plan': user.subscription_plan,
            'total_sessions': user.monitoring_sessions_count,
            'active_sessions': active_sessions,
            'completed_sessions': completed_sessions,
            'total_screenshots': user.total_screenshots,
            'total_changes_detected': total_changes,
            'max_sessions': user.max_monitoring_sessions,
            'can_start_session': user.can_start_monitoring_session(),
            'member_since': user.created_at.strftime('%B %Y'),
            'last_active': user.last_active
        }
    }, status=status.HTTP_200_OK)

class UserListView(generics.ListAPIView):
    """List all users (admin only)"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """User detail view (admin only)"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Avg, Count
from django.utils import timezone
from .models import MonitoringSession, Screenshot, ChangeDetection, OddsData, MonitoringAlert
from .serializers import (
    MonitoringSessionSerializer,
    MonitoringSessionCreateSerializer,
    MonitoringSessionListSerializer,
    ScreenshotSerializer,
    ChangeDetectionSerializer,
    OddsDataSerializer,
    MonitoringAlertSerializer,
    MonitoringStatsSerializer
)
import threading
import requests
import json

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def start_monitoring_session(request):
    """Start a new monitoring session"""
    user = request.user
    
    # Check if user can start a new session
    if not user.can_start_monitoring_session():
        return Response({
            'success': False,
            'error': f'Maximum sessions reached. You can have up to {user.max_monitoring_sessions} active sessions.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = MonitoringSessionCreateSerializer(data=request.data)
    if serializer.is_valid():
        session = serializer.save(user=user)
        
        # Start monitoring in background
        thread = threading.Thread(
            target=start_background_monitoring,
            args=(session.id,)
        )
        thread.daemon = True
        thread.start()
        
        # Update user session count
        user.monitoring_sessions_count += 1
        user.save()
        
        return Response({
            'success': True,
            'message': f'Monitoring session started for {session.site_url}',
            'session': MonitoringSessionSerializer(session).data
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def stop_monitoring_session(request, session_id):
    """Stop a monitoring session"""
    session = get_object_or_404(MonitoringSession, id=session_id, user=request.user)
    
    if session.status != 'active':
        return Response({
            'success': False,
            'error': 'Session is not active'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    session.stop_session()
    
    return Response({
        'success': True,
        'message': 'Monitoring session stopped',
        'session': MonitoringSessionSerializer(session).data
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def pause_monitoring_session(request, session_id):
    """Pause a monitoring session"""
    session = get_object_or_404(MonitoringSession, id=session_id, user=request.user)
    
    if session.status != 'active':
        return Response({
            'success': False,
            'error': 'Session is not active'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    session.pause_session()
    
    return Response({
        'success': True,
        'message': 'Monitoring session paused',
        'session': MonitoringSessionSerializer(session).data
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def resume_monitoring_session(request, session_id):
    """Resume a paused monitoring session"""
    session = get_object_or_404(MonitoringSession, id=session_id, user=request.user)
    
    if session.status != 'paused':
        return Response({
            'success': False,
            'error': 'Session is not paused'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    session.resume_session()
    
    # Restart monitoring in background
    thread = threading.Thread(
        target=start_background_monitoring,
        args=(session.id,)
    )
    thread.daemon = True
    thread.start()
    
    return Response({
        'success': True,
        'message': 'Monitoring session resumed',
        'session': MonitoringSessionSerializer(session).data
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_monitoring_sessions(request):
    """Get user's monitoring sessions"""
    sessions = MonitoringSession.objects.filter(user=request.user).order_by('-created_at')
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        sessions = sessions.filter(status=status_filter)
    
    # Pagination
    page_size = int(request.GET.get('page_size', 20))
    page = int(request.GET.get('page', 1))
    start = (page - 1) * page_size
    end = start + page_size
    
    total_count = sessions.count()
    sessions_page = sessions[start:end]
    
    return Response({
        'success': True,
        'sessions': MonitoringSessionListSerializer(sessions_page, many=True).data,
        'pagination': {
            'total': total_count,
            'page': page,
            'page_size': page_size,
            'has_next': end < total_count,
            'has_previous': page > 1
        }
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_monitoring_session(request, session_id):
    """Get detailed monitoring session"""
    session = get_object_or_404(MonitoringSession, id=session_id, user=request.user)
    
    return Response({
        'success': True,
        'session': MonitoringSessionSerializer(session).data
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_session_screenshots(request, session_id):
    """Get screenshots for a session"""
    session = get_object_or_404(MonitoringSession, id=session_id, user=request.user)
    screenshots = session.screenshots.order_by('-captured_at')
    
    # Pagination
    page_size = int(request.GET.get('page_size', 10))
    page = int(request.GET.get('page', 1))
    start = (page - 1) * page_size
    end = start + page_size
    
    total_count = screenshots.count()
    screenshots_page = screenshots[start:end]
    
    return Response({
        'success': True,
        'screenshots': ScreenshotSerializer(screenshots_page, many=True).data,
        'pagination': {
            'total': total_count,
            'page': page,
            'page_size': page_size,
            'has_next': end < total_count,
            'has_previous': page > 1
        }
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_monitoring_stats(request):
    """Get user's monitoring statistics"""
    user = request.user
    sessions = user.monitoring_sessions.all()
    
    # Calculate stats
    total_sessions = sessions.count()
    active_sessions = sessions.filter(status='active').count()
    completed_sessions = sessions.filter(status='completed').count()
    
    total_screenshots = sessions.aggregate(Sum('screenshots_count'))['screenshots_count__sum'] or 0
    total_changes = sessions.aggregate(Sum('changes_detected'))['changes_detected__sum'] or 0
    total_odds = sessions.aggregate(Sum('odds_captured'))['odds_captured__sum'] or 0
    
    # Calculate average session duration
    completed_with_end = sessions.filter(status='completed', end_time__isnull=False)
    avg_duration = 0
    if completed_with_end.exists():
        durations = []
        for session in completed_with_end:
            duration = (session.end_time - session.start_time).total_seconds() / 60
            durations.append(duration)
        avg_duration = sum(durations) / len(durations) if durations else 0
    
    # Most monitored site
    site_counts = sessions.values('site_url').annotate(count=Count('id')).order_by('-count')
    most_monitored_site = site_counts[0]['site_url'] if site_counts else 'None'
    
    # Success rate (sessions that completed successfully)
    success_rate = (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0
    
    stats_data = {
        'total_sessions': total_sessions,
        'active_sessions': active_sessions,
        'completed_sessions': completed_sessions,
        'total_screenshots': total_screenshots,
        'total_changes': total_changes,
        'total_odds': total_odds,
        'avg_session_duration': round(avg_duration, 2),
        'most_monitored_site': most_monitored_site,
        'success_rate': round(success_rate, 2)
    }
    
    return Response({
        'success': True,
        'stats': stats_data
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_user_alerts(request):
    """Get user's monitoring alerts"""
    alerts = MonitoringAlert.objects.filter(user=request.user).order_by('-created_at')
    
    # Filter by read status
    is_read = request.GET.get('is_read')
    if is_read is not None:
        alerts = alerts.filter(is_read=is_read.lower() == 'true')
    
    # Pagination
    page_size = int(request.GET.get('page_size', 20))
    page = int(request.GET.get('page', 1))
    start = (page - 1) * page_size
    end = start + page_size
    
    total_count = alerts.count()
    alerts_page = alerts[start:end]
    
    return Response({
        'success': True,
        'alerts': MonitoringAlertSerializer(alerts_page, many=True).data,
        'pagination': {
            'total': total_count,
            'page': page,
            'page_size': page_size,
            'has_next': end < total_count,
            'has_previous': page > 1
        }
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_alert_read(request, alert_id):
    """Mark an alert as read"""
    alert = get_object_or_404(MonitoringAlert, id=alert_id, user=request.user)
    alert.mark_as_read()
    
    return Response({
        'success': True,
        'message': 'Alert marked as read'
    }, status=status.HTTP_200_OK)

def start_background_monitoring(session_id):
    """Start background monitoring process"""
    try:
        # Call the existing improved visual monitor
        response = requests.post('http://localhost:5002/api/start-visual-monitoring', json={
            'url': MonitoringSession.objects.get(id=session_id).site_url,
            'interval': MonitoringSession.objects.get(id=session_id).monitoring_interval,
            'duration': MonitoringSession.objects.get(id=session_id).max_duration
        })
        
        if response.status_code == 200:
            print(f"✅ Background monitoring started for session {session_id}")
        else:
            print(f"❌ Failed to start background monitoring for session {session_id}")
            
    except Exception as e:
        print(f"❌ Background monitoring error: {e}")

# Class-based views for admin
class MonitoringSessionListView(generics.ListAPIView):
    """List all monitoring sessions (admin only)"""
    queryset = MonitoringSession.objects.all()
    serializer_class = MonitoringSessionListSerializer
    permission_classes = [permissions.IsAdminUser]

class ScreenshotListView(generics.ListAPIView):
    """List all screenshots (admin only)"""
    queryset = Screenshot.objects.all()
    serializer_class = ScreenshotSerializer
    permission_classes = [permissions.IsAdminUser]
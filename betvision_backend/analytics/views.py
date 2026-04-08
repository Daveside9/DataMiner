from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from datetime import datetime, timedelta
from .models import UserAnalytics, SiteAnalytics, DailyStats, PlatformMetrics

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_user_analytics(request):
    """Get user analytics data"""
    user = request.user
    
    # Get or create user analytics
    analytics, created = UserAnalytics.objects.get_or_create(user=user)
    
    if created or (timezone.now() - analytics.last_calculated).days > 0:
        analytics.recalculate_stats()
    
    return Response({
        'success': True,
        'analytics': {
            'total_sessions': analytics.total_sessions,
            'total_screenshots': analytics.total_screenshots,
            'total_monitoring_hours': analytics.total_monitoring_hours,
            'total_changes_detected': analytics.total_changes_detected,
            'total_odds_captured': analytics.total_odds_captured,
            'avg_session_duration': analytics.avg_session_duration,
            'avg_screenshots_per_session': analytics.avg_screenshots_per_session,
            'avg_changes_per_session': analytics.avg_changes_per_session,
            'most_monitored_site': analytics.most_monitored_site,
            'most_used_interval': analytics.most_used_interval,
            'preferred_quality': analytics.preferred_quality,
            'most_active_hour': analytics.most_active_hour,
            'most_active_day': analytics.most_active_day,
            'last_calculated': analytics.last_calculated
        }
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def recalculate_user_analytics(request):
    """Recalculate user analytics"""
    user = request.user
    
    analytics, created = UserAnalytics.objects.get_or_create(user=user)
    analytics.recalculate_stats()
    
    return Response({
        'success': True,
        'message': 'Analytics recalculated successfully'
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def get_platform_metrics(request):
    """Get platform-wide metrics (admin only)"""
    metrics = PlatformMetrics.update_metrics()
    
    return Response({
        'success': True,
        'metrics': {
            'total_registered_users': metrics.total_registered_users,
            'active_users_today': metrics.active_users_today,
            'active_users_week': metrics.active_users_week,
            'active_users_month': metrics.active_users_month,
            'free_users': metrics.free_users,
            'pro_users': metrics.pro_users,
            'enterprise_users': metrics.enterprise_users,
            'total_monitoring_sessions': metrics.total_monitoring_sessions,
            'total_screenshots_captured': metrics.total_screenshots_captured,
            'total_changes_detected': metrics.total_changes_detected,
            'total_monitoring_hours': metrics.total_monitoring_hours,
            'avg_screenshot_quality': metrics.avg_screenshot_quality,
            'system_uptime_percentage': metrics.system_uptime_percentage,
            'avg_response_time': metrics.avg_response_time,
            'most_monitored_sites': metrics.most_monitored_sites,
            'peak_usage_hours': metrics.peak_usage_hours,
            'last_updated': metrics.last_updated
        }
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def get_daily_stats(request, date):
    """Get daily statistics for a specific date (admin only)"""
    try:
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
        daily_stats = DailyStats.calculate_for_date(date_obj)
        
        return Response({
            'success': True,
            'stats': {
                'date': daily_stats.date,
                'active_users': daily_stats.active_users,
                'new_users': daily_stats.new_users,
                'total_users': daily_stats.total_users,
                'new_sessions': daily_stats.new_sessions,
                'completed_sessions': daily_stats.completed_sessions,
                'total_screenshots': daily_stats.total_screenshots,
                'total_changes_detected': daily_stats.total_changes_detected,
                'total_odds_captured': daily_stats.total_odds_captured,
                'avg_session_duration': daily_stats.avg_session_duration,
                'avg_screenshot_quality': daily_stats.avg_screenshot_quality,
                'system_uptime': daily_stats.system_uptime,
                'top_monitored_sites': daily_stats.top_monitored_sites
            }
        }, status=status.HTTP_200_OK)
        
    except ValueError:
        return Response({
            'success': False,
            'error': 'Invalid date format. Use YYYY-MM-DD'
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def get_site_analytics(request):
    """Get analytics for all monitored sites (admin only)"""
    sites = SiteAnalytics.objects.all().order_by('-total_sessions')[:20]
    
    site_data = []
    for site in sites:
        site.recalculate_stats()  # Ensure fresh data
        site_data.append({
            'site_url': site.site_url,
            'site_name': site.site_name,
            'total_sessions': site.total_sessions,
            'total_users': site.total_users,
            'total_screenshots': site.total_screenshots,
            'total_monitoring_hours': site.total_monitoring_hours,
            'avg_screenshot_quality': site.avg_screenshot_quality,
            'avg_odds_per_screenshot': site.avg_odds_per_screenshot,
            'avg_changes_per_hour': site.avg_changes_per_hour,
            'success_rate': site.success_rate,
            'most_used_interval': site.most_used_interval,
            'most_used_quality': site.most_used_quality,
            'first_monitored': site.first_monitored,
            'last_monitored': site.last_monitored
        })
    
    return Response({
        'success': True,
        'sites': site_data
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_dashboard_data(request):
    """Get dashboard data for the user"""
    user = request.user
    
    # User analytics
    analytics, created = UserAnalytics.objects.get_or_create(user=user)
    if created or (timezone.now() - analytics.last_calculated).days > 0:
        analytics.recalculate_stats()
    
    # Recent sessions
    recent_sessions = user.monitoring_sessions.order_by('-created_at')[:5]
    
    # Active sessions
    active_sessions = user.monitoring_sessions.filter(status='active')
    
    # Recent alerts
    recent_alerts = user.monitoring_alerts.filter(is_read=False).order_by('-created_at')[:5]
    
    # Usage this week
    week_ago = timezone.now() - timedelta(days=7)
    sessions_this_week = user.monitoring_sessions.filter(created_at__gte=week_ago).count()
    
    return Response({
        'success': True,
        'dashboard': {
            'user_info': {
                'full_name': user.full_name,
                'subscription_plan': user.subscription_plan,
                'member_since': user.created_at.strftime('%B %Y'),
                'max_sessions': user.max_monitoring_sessions
            },
            'quick_stats': {
                'total_sessions': analytics.total_sessions,
                'active_sessions': active_sessions.count(),
                'total_screenshots': analytics.total_screenshots,
                'sessions_this_week': sessions_this_week,
                'unread_alerts': recent_alerts.count()
            },
            'recent_sessions': [
                {
                    'id': session.id,
                    'site_name': session.site_name or session.site_url,
                    'status': session.status,
                    'start_time': session.start_time,
                    'screenshots_count': session.screenshots_count,
                    'changes_detected': session.changes_detected
                }
                for session in recent_sessions
            ],
            'active_sessions': [
                {
                    'id': session.id,
                    'site_name': session.site_name or session.site_url,
                    'start_time': session.start_time,
                    'screenshots_count': session.screenshots_count,
                    'monitoring_interval': session.monitoring_interval
                }
                for session in active_sessions
            ],
            'recent_alerts': [
                {
                    'id': alert.id,
                    'title': alert.title,
                    'message': alert.message,
                    'priority': alert.priority,
                    'created_at': alert.created_at
                }
                for alert in recent_alerts
            ],
            'analytics': {
                'avg_session_duration': analytics.avg_session_duration,
                'most_monitored_site': analytics.most_monitored_site,
                'total_monitoring_hours': analytics.total_monitoring_hours,
                'preferred_quality': analytics.preferred_quality
            }
        }
    }, status=status.HTTP_200_OK)
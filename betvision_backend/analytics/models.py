from django.db import models
from django.utils import timezone
from authentication.models import User
from monitoring.models import MonitoringSession, Screenshot
from django.db.models import Avg, Count, Sum

class UserAnalytics(models.Model):
    """Analytics data for users"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='analytics')
    
    # Usage statistics
    total_sessions = models.IntegerField(default=0)
    total_screenshots = models.IntegerField(default=0)
    total_monitoring_hours = models.FloatField(default=0.0)
    total_changes_detected = models.IntegerField(default=0)
    total_odds_captured = models.IntegerField(default=0)
    
    # Averages
    avg_session_duration = models.FloatField(default=0.0)  # in minutes
    avg_screenshots_per_session = models.FloatField(default=0.0)
    avg_changes_per_session = models.FloatField(default=0.0)
    
    # Most used
    most_monitored_site = models.URLField(blank=True)
    most_used_interval = models.IntegerField(default=30)  # seconds
    preferred_quality = models.CharField(max_length=20, default='high')
    
    # Activity patterns
    most_active_hour = models.IntegerField(null=True, blank=True)  # 0-23
    most_active_day = models.IntegerField(null=True, blank=True)   # 0-6 (Monday=0)
    
    # Last updated
    last_calculated = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'betvision_user_analytics'
    
    def __str__(self):
        return f"Analytics for {self.user.username}"
    
    def recalculate_stats(self):
        """Recalculate all analytics statistics"""
        sessions = self.user.monitoring_sessions.all()
        
        self.total_sessions = sessions.count()
        self.total_screenshots = sessions.aggregate(Sum('screenshots_count'))['screenshots_count__sum'] or 0
        self.total_changes_detected = sessions.aggregate(Sum('changes_detected'))['changes_detected__sum'] or 0
        self.total_odds_captured = sessions.aggregate(Sum('odds_captured'))['odds_captured__sum'] or 0
        
        # Calculate averages
        if self.total_sessions > 0:
            completed_sessions = sessions.filter(status='completed')
            if completed_sessions.exists():
                durations = []
                for session in completed_sessions:
                    if session.end_time:
                        duration = (session.end_time - session.start_time).total_seconds() / 60
                        durations.append(duration)
                
                if durations:
                    self.avg_session_duration = sum(durations) / len(durations)
                    self.total_monitoring_hours = sum(durations) / 60
            
            self.avg_screenshots_per_session = self.total_screenshots / self.total_sessions
            self.avg_changes_per_session = self.total_changes_detected / self.total_sessions
        
        # Find most monitored site
        site_counts = sessions.values('site_url').annotate(count=Count('id')).order_by('-count')
        if site_counts:
            self.most_monitored_site = site_counts[0]['site_url']
        
        # Find most used interval
        interval_counts = sessions.values('monitoring_interval').annotate(count=Count('id')).order_by('-count')
        if interval_counts:
            self.most_used_interval = interval_counts[0]['monitoring_interval']
        
        self.save()


class SiteAnalytics(models.Model):
    """Analytics for monitored betting sites"""
    
    site_url = models.URLField(unique=True)
    site_name = models.CharField(max_length=255, blank=True)
    
    # Usage statistics
    total_sessions = models.IntegerField(default=0)
    total_users = models.IntegerField(default=0)
    total_screenshots = models.IntegerField(default=0)
    total_monitoring_hours = models.FloatField(default=0.0)
    
    # Performance metrics
    avg_screenshot_quality = models.FloatField(default=0.0)
    avg_odds_per_screenshot = models.FloatField(default=0.0)
    avg_changes_per_hour = models.FloatField(default=0.0)
    success_rate = models.FloatField(default=0.0)  # Percentage of successful screenshots
    
    # Popular settings
    most_used_interval = models.IntegerField(default=30)
    most_used_quality = models.CharField(max_length=20, default='high')
    
    # Timestamps
    first_monitored = models.DateTimeField(null=True, blank=True)
    last_monitored = models.DateTimeField(null=True, blank=True)
    last_calculated = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'betvision_site_analytics'
        ordering = ['-total_sessions']
    
    def __str__(self):
        return f"Analytics for {self.site_name or self.site_url}"
    
    def recalculate_stats(self):
        """Recalculate analytics for this site"""
        sessions = MonitoringSession.objects.filter(site_url=self.site_url)
        
        self.total_sessions = sessions.count()
        self.total_users = sessions.values('user').distinct().count()
        self.total_screenshots = sessions.aggregate(Sum('screenshots_count'))['screenshots_count__sum'] or 0
        
        # Calculate monitoring hours
        completed_sessions = sessions.filter(status='completed', end_time__isnull=False)
        total_minutes = 0
        for session in completed_sessions:
            duration = (session.end_time - session.start_time).total_seconds() / 60
            total_minutes += duration
        self.total_monitoring_hours = total_minutes / 60
        
        # Calculate averages
        screenshots = Screenshot.objects.filter(session__site_url=self.site_url)
        if screenshots.exists():
            quality_map = {'poor': 1, 'good': 2, 'excellent': 3}
            quality_scores = [quality_map.get(s.quality, 2) for s in screenshots]
            self.avg_screenshot_quality = sum(quality_scores) / len(quality_scores)
            
            self.avg_odds_per_screenshot = screenshots.aggregate(Avg('odds_detected'))['odds_detected__avg'] or 0
        
        # Success rate
        if self.total_screenshots > 0:
            successful_screenshots = screenshots.filter(page_load_success=True).count()
            self.success_rate = (successful_screenshots / self.total_screenshots) * 100
        
        # Timestamps
        if sessions.exists():
            self.first_monitored = sessions.order_by('start_time').first().start_time
            self.last_monitored = sessions.order_by('-start_time').first().start_time
        
        self.save()


class DailyStats(models.Model):
    """Daily statistics for the platform"""
    
    date = models.DateField(unique=True)
    
    # User activity
    active_users = models.IntegerField(default=0)
    new_users = models.IntegerField(default=0)
    total_users = models.IntegerField(default=0)
    
    # Monitoring activity
    new_sessions = models.IntegerField(default=0)
    completed_sessions = models.IntegerField(default=0)
    total_screenshots = models.IntegerField(default=0)
    total_changes_detected = models.IntegerField(default=0)
    total_odds_captured = models.IntegerField(default=0)
    
    # Performance metrics
    avg_session_duration = models.FloatField(default=0.0)
    avg_screenshot_quality = models.FloatField(default=0.0)
    system_uptime = models.FloatField(default=100.0)  # Percentage
    
    # Popular sites
    top_monitored_sites = models.JSONField(default=list, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'betvision_daily_stats'
        ordering = ['-date']
    
    def __str__(self):
        return f"Daily Stats for {self.date}"
    
    @classmethod
    def calculate_for_date(cls, date):
        """Calculate daily stats for a specific date"""
        start_of_day = timezone.datetime.combine(date, timezone.datetime.min.time())
        end_of_day = timezone.datetime.combine(date, timezone.datetime.max.time())
        
        # Make timezone aware
        start_of_day = timezone.make_aware(start_of_day)
        end_of_day = timezone.make_aware(end_of_day)
        
        # User activity
        active_users = User.objects.filter(
            last_active__range=(start_of_day, end_of_day)
        ).count()
        
        new_users = User.objects.filter(
            date_joined__range=(start_of_day, end_of_day)
        ).count()
        
        total_users = User.objects.filter(date_joined__lte=end_of_day).count()
        
        # Monitoring activity
        sessions_today = MonitoringSession.objects.filter(
            start_time__range=(start_of_day, end_of_day)
        )
        
        new_sessions = sessions_today.count()
        completed_sessions = sessions_today.filter(status='completed').count()
        
        total_screenshots = sessions_today.aggregate(
            Sum('screenshots_count')
        )['screenshots_count__sum'] or 0
        
        total_changes_detected = sessions_today.aggregate(
            Sum('changes_detected')
        )['changes_detected__sum'] or 0
        
        total_odds_captured = sessions_today.aggregate(
            Sum('odds_captured')
        )['odds_captured__sum'] or 0
        
        # Calculate averages
        avg_session_duration = 0.0
        completed_sessions_with_end = sessions_today.filter(
            status='completed', 
            end_time__isnull=False
        )
        
        if completed_sessions_with_end.exists():
            durations = []
            for session in completed_sessions_with_end:
                duration = (session.end_time - session.start_time).total_seconds() / 60
                durations.append(duration)
            avg_session_duration = sum(durations) / len(durations)
        
        # Screenshot quality
        screenshots_today = Screenshot.objects.filter(
            captured_at__range=(start_of_day, end_of_day)
        )
        
        avg_screenshot_quality = 0.0
        if screenshots_today.exists():
            quality_map = {'poor': 1, 'good': 2, 'excellent': 3}
            quality_scores = [quality_map.get(s.quality, 2) for s in screenshots_today]
            avg_screenshot_quality = sum(quality_scores) / len(quality_scores)
        
        # Top monitored sites
        top_sites = sessions_today.values('site_url', 'site_name').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        top_monitored_sites = [
            {'url': site['site_url'], 'name': site['site_name'], 'count': site['count']}
            for site in top_sites
        ]
        
        # Create or update daily stats
        daily_stats, created = cls.objects.get_or_create(
            date=date,
            defaults={
                'active_users': active_users,
                'new_users': new_users,
                'total_users': total_users,
                'new_sessions': new_sessions,
                'completed_sessions': completed_sessions,
                'total_screenshots': total_screenshots,
                'total_changes_detected': total_changes_detected,
                'total_odds_captured': total_odds_captured,
                'avg_session_duration': avg_session_duration,
                'avg_screenshot_quality': avg_screenshot_quality,
                'top_monitored_sites': top_monitored_sites,
            }
        )
        
        if not created:
            # Update existing record
            daily_stats.active_users = active_users
            daily_stats.new_users = new_users
            daily_stats.total_users = total_users
            daily_stats.new_sessions = new_sessions
            daily_stats.completed_sessions = completed_sessions
            daily_stats.total_screenshots = total_screenshots
            daily_stats.total_changes_detected = total_changes_detected
            daily_stats.total_odds_captured = total_odds_captured
            daily_stats.avg_session_duration = avg_session_duration
            daily_stats.avg_screenshot_quality = avg_screenshot_quality
            daily_stats.top_monitored_sites = top_monitored_sites
            daily_stats.save()
        
        return daily_stats


class PlatformMetrics(models.Model):
    """Overall platform metrics and KPIs"""
    
    # User metrics
    total_registered_users = models.IntegerField(default=0)
    active_users_today = models.IntegerField(default=0)
    active_users_week = models.IntegerField(default=0)
    active_users_month = models.IntegerField(default=0)
    
    # Subscription metrics
    free_users = models.IntegerField(default=0)
    pro_users = models.IntegerField(default=0)
    enterprise_users = models.IntegerField(default=0)
    
    # Usage metrics
    total_monitoring_sessions = models.IntegerField(default=0)
    total_screenshots_captured = models.IntegerField(default=0)
    total_changes_detected = models.IntegerField(default=0)
    total_monitoring_hours = models.FloatField(default=0.0)
    
    # Performance metrics
    avg_screenshot_quality = models.FloatField(default=0.0)
    system_uptime_percentage = models.FloatField(default=100.0)
    avg_response_time = models.FloatField(default=0.0)  # in seconds
    
    # Popular data
    most_monitored_sites = models.JSONField(default=list, blank=True)
    peak_usage_hours = models.JSONField(default=list, blank=True)
    
    # Timestamps
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'betvision_platform_metrics'
    
    def __str__(self):
        return f"Platform Metrics - {self.last_updated.date()}"
    
    @classmethod
    def update_metrics(cls):
        """Update platform metrics"""
        now = timezone.now()
        today = now.date()
        week_ago = now - timezone.timedelta(days=7)
        month_ago = now - timezone.timedelta(days=30)
        
        # User metrics
        total_registered_users = User.objects.count()
        active_users_today = User.objects.filter(last_active__date=today).count()
        active_users_week = User.objects.filter(last_active__gte=week_ago).count()
        active_users_month = User.objects.filter(last_active__gte=month_ago).count()
        
        # Subscription metrics
        free_users = User.objects.filter(subscription_plan='free').count()
        pro_users = User.objects.filter(subscription_plan='pro').count()
        enterprise_users = User.objects.filter(subscription_plan='enterprise').count()
        
        # Usage metrics
        total_monitoring_sessions = MonitoringSession.objects.count()
        total_screenshots_captured = Screenshot.objects.count()
        
        total_changes_detected = MonitoringSession.objects.aggregate(
            Sum('changes_detected')
        )['changes_detected__sum'] or 0
        
        # Calculate total monitoring hours
        completed_sessions = MonitoringSession.objects.filter(
            status='completed', 
            end_time__isnull=False
        )
        
        total_minutes = 0
        for session in completed_sessions:
            duration = (session.end_time - session.start_time).total_seconds() / 60
            total_minutes += duration
        total_monitoring_hours = total_minutes / 60
        
        # Performance metrics
        screenshots = Screenshot.objects.all()
        avg_screenshot_quality = 0.0
        if screenshots.exists():
            quality_map = {'poor': 1, 'good': 2, 'excellent': 3}
            quality_scores = [quality_map.get(s.quality, 2) for s in screenshots]
            avg_screenshot_quality = sum(quality_scores) / len(quality_scores)
        
        # Most monitored sites
        top_sites = MonitoringSession.objects.values('site_url').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        most_monitored_sites = [
            {'url': site['site_url'], 'count': site['count']}
            for site in top_sites
        ]
        
        # Create or update metrics
        metrics, created = cls.objects.get_or_create(
            id=1,  # Single record
            defaults={
                'total_registered_users': total_registered_users,
                'active_users_today': active_users_today,
                'active_users_week': active_users_week,
                'active_users_month': active_users_month,
                'free_users': free_users,
                'pro_users': pro_users,
                'enterprise_users': enterprise_users,
                'total_monitoring_sessions': total_monitoring_sessions,
                'total_screenshots_captured': total_screenshots_captured,
                'total_changes_detected': total_changes_detected,
                'total_monitoring_hours': total_monitoring_hours,
                'avg_screenshot_quality': avg_screenshot_quality,
                'most_monitored_sites': most_monitored_sites,
            }
        )
        
        if not created:
            # Update existing record
            metrics.total_registered_users = total_registered_users
            metrics.active_users_today = active_users_today
            metrics.active_users_week = active_users_week
            metrics.active_users_month = active_users_month
            metrics.free_users = free_users
            metrics.pro_users = pro_users
            metrics.enterprise_users = enterprise_users
            metrics.total_monitoring_sessions = total_monitoring_sessions
            metrics.total_screenshots_captured = total_screenshots_captured
            metrics.total_changes_detected = total_changes_detected
            metrics.total_monitoring_hours = total_monitoring_hours
            metrics.avg_screenshot_quality = avg_screenshot_quality
            metrics.most_monitored_sites = most_monitored_sites
            metrics.save()
        
        return metrics
from django.db import models
from django.utils import timezone
from authentication.models import User
import json

class MonitoringSession(models.Model):
    """Represents a betting site monitoring session"""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='monitoring_sessions')
    
    # Session details
    site_url = models.URLField()
    site_name = models.CharField(max_length=255, blank=True)
    session_name = models.CharField(max_length=255, blank=True)
    
    # Monitoring configuration
    monitoring_interval = models.IntegerField(default=30)  # seconds
    max_duration = models.IntegerField(default=60)  # minutes
    screenshot_quality = models.CharField(
        max_length=20,
        choices=[('standard', 'Standard'), ('high', 'High'), ('ultra', 'Ultra')],
        default='high'
    )
    
    # Status and timing
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    last_screenshot_time = models.DateTimeField(null=True, blank=True)
    
    # Statistics
    screenshots_count = models.IntegerField(default=0)
    changes_detected = models.IntegerField(default=0)
    odds_captured = models.IntegerField(default=0)
    errors_count = models.IntegerField(default=0)
    
    # Configuration
    focus_areas = models.JSONField(default=list, blank=True)  # Areas to focus monitoring on
    alert_keywords = models.JSONField(default=list, blank=True)  # Keywords to alert on
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'betvision_monitoring_sessions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.site_name or self.site_url} ({self.status})"
    
    @property
    def duration(self):
        """Get session duration"""
        if self.end_time:
            return self.end_time - self.start_time
        return timezone.now() - self.start_time
    
    @property
    def is_active(self):
        return self.status == 'active'
    
    def stop_session(self):
        """Stop the monitoring session"""
        self.status = 'completed'
        self.end_time = timezone.now()
        self.save()
    
    def pause_session(self):
        """Pause the monitoring session"""
        self.status = 'paused'
        self.save()
    
    def resume_session(self):
        """Resume the monitoring session"""
        self.status = 'active'
        self.save()


class Screenshot(models.Model):
    """Represents a captured screenshot"""
    
    QUALITY_CHOICES = [
        ('poor', 'Poor'),
        ('good', 'Good'),
        ('excellent', 'Excellent'),
    ]
    
    session = models.ForeignKey(MonitoringSession, on_delete=models.CASCADE, related_name='screenshots')
    
    # File information
    image = models.ImageField(upload_to='screenshots/%Y/%m/%d/')
    thumbnail = models.ImageField(upload_to='thumbnails/%Y/%m/%d/', null=True, blank=True)
    filename = models.CharField(max_length=255)
    file_size = models.IntegerField()  # in bytes
    
    # Screenshot metadata
    quality = models.CharField(max_length=20, choices=QUALITY_CHOICES, default='good')
    width = models.IntegerField()
    height = models.IntegerField()
    
    # Analysis results
    odds_detected = models.IntegerField(default=0)
    live_matches_detected = models.IntegerField(default=0)
    page_elements_count = models.IntegerField(default=0)
    page_load_success = models.BooleanField(default=True)
    
    # Content analysis
    extracted_text = models.TextField(blank=True)
    detected_odds = models.JSONField(default=dict, blank=True)
    live_indicators = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    captured_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'betvision_screenshots'
        ordering = ['-captured_at']
    
    def __str__(self):
        return f"Screenshot {self.filename} - {self.captured_at}"
    
    @property
    def file_size_mb(self):
        """Get file size in MB"""
        return round(self.file_size / (1024 * 1024), 2)


class ChangeDetection(models.Model):
    """Represents detected changes between screenshots"""
    
    CHANGE_TYPES = [
        ('visual', 'Visual Change'),
        ('odds', 'Odds Change'),
        ('content', 'Content Change'),
        ('layout', 'Layout Change'),
    ]
    
    SEVERITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    session = models.ForeignKey(MonitoringSession, on_delete=models.CASCADE, related_name='changes')
    current_screenshot = models.ForeignKey(Screenshot, on_delete=models.CASCADE, related_name='changes_as_current')
    previous_screenshot = models.ForeignKey(Screenshot, on_delete=models.CASCADE, related_name='changes_as_previous')
    
    # Change details
    change_type = models.CharField(max_length=20, choices=CHANGE_TYPES, default='visual')
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS, default='medium')
    change_percentage = models.FloatField()  # Percentage of image that changed
    
    # Description and analysis
    description = models.TextField()
    affected_areas = models.JSONField(default=list, blank=True)  # Areas of the image that changed
    
    # Metadata
    detected_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'betvision_change_detections'
        ordering = ['-detected_at']
    
    def __str__(self):
        return f"{self.change_type} change - {self.change_percentage}% ({self.severity})"


class OddsData(models.Model):
    """Represents extracted odds data"""
    
    ODDS_TYPES = [
        ('decimal', 'Decimal'),
        ('fractional', 'Fractional'),
        ('american_plus', 'American (+)'),
        ('american_minus', 'American (-)'),
    ]
    
    screenshot = models.ForeignKey(Screenshot, on_delete=models.CASCADE, related_name='odds_data')
    session = models.ForeignKey(MonitoringSession, on_delete=models.CASCADE, related_name='odds_data')
    
    # Odds information
    odds_type = models.CharField(max_length=20, choices=ODDS_TYPES)
    odds_value = models.CharField(max_length=50)
    
    # Context
    match_info = models.CharField(max_length=255, blank=True)  # e.g., "Arsenal vs Chelsea"
    bet_type = models.CharField(max_length=100, blank=True)   # e.g., "Match Winner", "Over/Under"
    
    # Position in screenshot
    position_x = models.IntegerField(null=True, blank=True)
    position_y = models.IntegerField(null=True, blank=True)
    
    # Metadata
    extracted_at = models.DateTimeField(auto_now_add=True)
    confidence_score = models.FloatField(default=0.0)  # AI confidence in extraction
    
    class Meta:
        db_table = 'betvision_odds_data'
        ordering = ['-extracted_at']
    
    def __str__(self):
        return f"{self.odds_value} ({self.odds_type}) - {self.match_info}"


class MonitoringAlert(models.Model):
    """Represents alerts triggered during monitoring"""
    
    ALERT_TYPES = [
        ('odds_change', 'Odds Change'),
        ('new_match', 'New Match'),
        ('keyword_detected', 'Keyword Detected'),
        ('error', 'Error'),
        ('threshold_reached', 'Threshold Reached'),
    ]
    
    PRIORITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    session = models.ForeignKey(MonitoringSession, on_delete=models.CASCADE, related_name='alerts')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='monitoring_alerts')
    
    # Alert details
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    priority = models.CharField(max_length=20, choices=PRIORITY_LEVELS, default='medium')
    title = models.CharField(max_length=255)
    message = models.TextField()
    
    # Related data
    related_screenshot = models.ForeignKey(Screenshot, on_delete=models.SET_NULL, null=True, blank=True)
    trigger_data = models.JSONField(default=dict, blank=True)  # Data that triggered the alert
    
    # Status
    is_read = models.BooleanField(default=False)
    is_dismissed = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'betvision_monitoring_alerts'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.priority})"
    
    def mark_as_read(self):
        """Mark alert as read"""
        self.is_read = True
        self.read_at = timezone.now()
        self.save()
    
    def dismiss(self):
        """Dismiss the alert"""
        self.is_dismissed = True
        self.save()
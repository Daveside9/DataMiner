from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    """Custom User model for BetVision Pro"""
    
    SUBSCRIPTION_CHOICES = [
        ('free', 'Free'),
        ('pro', 'Pro'),
        ('enterprise', 'Enterprise'),
    ]
    
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    subscription_plan = models.CharField(
        max_length=20, 
        choices=SUBSCRIPTION_CHOICES, 
        default='free'
    )
    
    # Usage tracking
    monitoring_sessions_count = models.IntegerField(default=0)
    total_screenshots = models.IntegerField(default=0)
    total_monitoring_time = models.DurationField(default=timezone.timedelta)
    
    # Profile info
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    website = models.URLField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    
    # Preferences
    email_notifications = models.BooleanField(default=True)
    default_monitoring_interval = models.IntegerField(default=30)  # seconds
    preferred_betting_sites = models.JSONField(default=list, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_active = models.DateTimeField(default=timezone.now)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'full_name']
    
    class Meta:
        db_table = 'betvision_users'
        verbose_name = 'BetVision User'
        verbose_name_plural = 'BetVision Users'
    
    def __str__(self):
        return f"{self.full_name} ({self.email})"
    
    @property
    def is_pro_user(self):
        return self.subscription_plan in ['pro', 'enterprise']
    
    @property
    def max_monitoring_sessions(self):
        if self.subscription_plan == 'free':
            return 5
        elif self.subscription_plan == 'pro':
            return 50
        else:  # enterprise
            return 200
    
    def can_start_monitoring_session(self):
        """Check if user can start a new monitoring session"""
        active_sessions = self.monitoring_sessions.filter(status='active').count()
        return active_sessions < self.max_monitoring_sessions
    
    def update_last_active(self):
        """Update last active timestamp"""
        self.last_active = timezone.now()
        self.save(update_fields=['last_active'])


class UserProfile(models.Model):
    """Extended user profile information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Subscription details
    subscription_start_date = models.DateTimeField(null=True, blank=True)
    subscription_end_date = models.DateTimeField(null=True, blank=True)
    auto_renew = models.BooleanField(default=False)
    
    # Usage statistics
    total_monitoring_hours = models.FloatField(default=0.0)
    favorite_betting_sites = models.JSONField(default=list, blank=True)
    most_monitored_site = models.URLField(blank=True)
    
    # Settings
    dashboard_theme = models.CharField(
        max_length=20, 
        choices=[('light', 'Light'), ('dark', 'Dark')], 
        default='light'
    )
    timezone = models.CharField(max_length=50, default='UTC')
    language = models.CharField(max_length=10, default='en')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'betvision_user_profiles'
    
    def __str__(self):
        return f"{self.user.full_name}'s Profile"
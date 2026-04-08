from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class BettingSite(models.Model):
    """Model for supported betting sites"""
    name = models.CharField(max_length=100)
    url = models.URLField()
    login_required = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class ExtractionSession(models.Model):
    """Model for extraction sessions"""
    STATUS_CHOICES = [
        ('starting', 'Starting'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('error', 'Error'),
        ('stopped', 'Stopped'),
    ]
    
    session_id = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    site = models.ForeignKey(BettingSite, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='starting')
    progress = models.IntegerField(default=0)
    message = models.TextField(blank=True)
    max_matches = models.IntegerField(default=25)
    matches_found = models.IntegerField(default=0)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.session_id} - {self.site.name}"

class MatchResult(models.Model):
    """Model for extracted match results"""
    RESULT_CHOICES = [
        ('home_win', 'Home Win'),
        ('away_win', 'Away Win'),
        ('draw', 'Draw'),
    ]
    
    session = models.ForeignKey(ExtractionSession, on_delete=models.CASCADE, related_name='results')
    match_id = models.CharField(max_length=100)
    date = models.DateField()
    home_team = models.CharField(max_length=100)
    away_team = models.CharField(max_length=100)
    home_score = models.IntegerField()
    away_score = models.IntegerField()
    competition = models.CharField(max_length=100, blank=True)
    result_type = models.CharField(max_length=20, choices=RESULT_CHOICES)
    confidence_score = models.FloatField()
    screenshot_path = models.CharField(max_length=500, blank=True)
    betting_odds = models.JSONField(default=dict, blank=True)
    extracted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['session', 'match_id']
    
    def __str__(self):
        return f"{self.home_team} vs {self.away_team} ({self.date})"

class ExtractionConfig(models.Model):
    """Model for extraction configuration"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ocr_engine = models.CharField(max_length=20, default='easyocr')
    enhance_contrast = models.BooleanField(default=True)
    denoise = models.BooleanField(default=True)
    sharpen = models.BooleanField(default=True)
    threshold = models.BooleanField(default=True)
    headless_mode = models.BooleanField(default=False)
    save_screenshots = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Config for {self.user.username}"
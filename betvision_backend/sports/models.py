from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class SportsMatch(models.Model):
    """Model for storing sports match data"""
    SPORT_CHOICES = [
        ('football', 'Football/Soccer'),
        ('basketball', 'Basketball'),
        ('tennis', 'Tennis'),
        ('baseball', 'Baseball'),
        ('hockey', 'Hockey'),
    ]
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('live', 'Live'),
        ('finished', 'Finished'),
        ('postponed', 'Postponed'),
        ('cancelled', 'Cancelled'),
    ]
    
    sport = models.CharField(max_length=20, choices=SPORT_CHOICES)
    home_team = models.CharField(max_length=100)
    away_team = models.CharField(max_length=100)
    home_score = models.IntegerField(default=0)
    away_score = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    match_time = models.DateTimeField()
    source_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-match_time']
    
    def __str__(self):
        return f"{self.home_team} vs {self.away_team} ({self.sport})"

class SportsMonitoringSession(models.Model):
    """Model for sports monitoring sessions"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sports_sessions')
    sport = models.CharField(max_length=20, choices=SportsMatch.SPORT_CHOICES)
    source_url = models.URLField()
    teams_filter = models.TextField(blank=True, help_text="Comma-separated team names to monitor")
    interval_seconds = models.IntegerField(default=60)
    duration_minutes = models.IntegerField(default=30)
    status = models.CharField(max_length=20, choices=[
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ], default='active')
    matches_found = models.IntegerField(default=0)
    predictions_generated = models.IntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.sport} monitoring"

class MatchPrediction(models.Model):
    """Model for storing AI match predictions"""
    match = models.ForeignKey(SportsMatch, on_delete=models.CASCADE, related_name='predictions')
    session = models.ForeignKey(SportsMonitoringSession, on_delete=models.CASCADE, related_name='predictions')
    predicted_home_score = models.IntegerField()
    predicted_away_score = models.IntegerField()
    confidence_percentage = models.FloatField()
    reasoning = models.TextField()
    prediction_factors = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Prediction: {self.match} - {self.predicted_home_score}-{self.predicted_away_score} ({self.confidence_percentage}%)"

class TeamAnalysis(models.Model):
    """Model for storing team analysis data"""
    team_name = models.CharField(max_length=100)
    sport = models.CharField(max_length=20, choices=SportsMatch.SPORT_CHOICES)
    analysis_data = models.JSONField(default=dict)
    recent_form = models.JSONField(default=dict)
    key_stats = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['team_name', 'sport']
    
    def __str__(self):
        return f"{self.team_name} ({self.sport}) Analysis"
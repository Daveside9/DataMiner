from rest_framework import serializers
from .models import MonitoringSession, Screenshot, ChangeDetection, OddsData, MonitoringAlert

class ScreenshotSerializer(serializers.ModelSerializer):
    """Serializer for screenshots"""
    file_size_mb = serializers.ReadOnlyField()
    
    class Meta:
        model = Screenshot
        fields = '__all__'
        read_only_fields = ('session', 'captured_at')

class ChangeDetectionSerializer(serializers.ModelSerializer):
    """Serializer for change detection"""
    
    class Meta:
        model = ChangeDetection
        fields = '__all__'
        read_only_fields = ('session', 'detected_at')

class OddsDataSerializer(serializers.ModelSerializer):
    """Serializer for odds data"""
    
    class Meta:
        model = OddsData
        fields = '__all__'
        read_only_fields = ('session', 'screenshot', 'extracted_at')

class MonitoringAlertSerializer(serializers.ModelSerializer):
    """Serializer for monitoring alerts"""
    
    class Meta:
        model = MonitoringAlert
        fields = '__all__'
        read_only_fields = ('session', 'user', 'created_at')

class MonitoringSessionSerializer(serializers.ModelSerializer):
    """Serializer for monitoring sessions"""
    duration = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()
    screenshots = ScreenshotSerializer(many=True, read_only=True)
    changes = ChangeDetectionSerializer(many=True, read_only=True)
    odds_data = OddsDataSerializer(many=True, read_only=True)
    alerts = MonitoringAlertSerializer(many=True, read_only=True)
    
    class Meta:
        model = MonitoringSession
        fields = '__all__'
        read_only_fields = ('user', 'start_time', 'end_time', 'last_screenshot_time', 
                           'screenshots_count', 'changes_detected', 'odds_captured', 
                           'errors_count', 'created_at', 'updated_at')

class MonitoringSessionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating monitoring sessions"""
    
    class Meta:
        model = MonitoringSession
        fields = ('site_url', 'site_name', 'session_name', 'monitoring_interval', 
                 'max_duration', 'screenshot_quality', 'focus_areas', 'alert_keywords')
    
    def validate_site_url(self, value):
        """Validate site URL"""
        if not value.startswith(('http://', 'https://')):
            raise serializers.ValidationError("URL must start with http:// or https://")
        return value
    
    def validate_monitoring_interval(self, value):
        """Validate monitoring interval"""
        if value < 10:
            raise serializers.ValidationError("Monitoring interval must be at least 10 seconds")
        if value > 300:
            raise serializers.ValidationError("Monitoring interval cannot exceed 300 seconds")
        return value
    
    def validate_max_duration(self, value):
        """Validate max duration"""
        if value < 1:
            raise serializers.ValidationError("Duration must be at least 1 minute")
        if value > 480:  # 8 hours
            raise serializers.ValidationError("Duration cannot exceed 480 minutes")
        return value

class MonitoringSessionListSerializer(serializers.ModelSerializer):
    """Simplified serializer for session lists"""
    duration = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()
    
    class Meta:
        model = MonitoringSession
        fields = ('id', 'site_url', 'site_name', 'session_name', 'status', 
                 'start_time', 'end_time', 'duration', 'is_active', 
                 'screenshots_count', 'changes_detected', 'odds_captured')

class MonitoringStatsSerializer(serializers.Serializer):
    """Serializer for monitoring statistics"""
    total_sessions = serializers.IntegerField()
    active_sessions = serializers.IntegerField()
    completed_sessions = serializers.IntegerField()
    total_screenshots = serializers.IntegerField()
    total_changes = serializers.IntegerField()
    total_odds = serializers.IntegerField()
    avg_session_duration = serializers.FloatField()
    most_monitored_site = serializers.CharField()
    success_rate = serializers.FloatField()
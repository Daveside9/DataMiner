from django.contrib import admin
from .models import MonitoringSession, Screenshot, ChangeDetection, OddsData, MonitoringAlert

@admin.register(MonitoringSession)
class MonitoringSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'site_name', 'site_url', 'status', 'start_time', 'screenshots_count', 'changes_detected')
    list_filter = ('status', 'screenshot_quality', 'created_at')
    search_fields = ('user__email', 'site_url', 'site_name', 'session_name')
    readonly_fields = ('created_at', 'updated_at', 'duration')
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('user', 'site_url', 'site_name', 'session_name')
        }),
        ('Configuration', {
            'fields': ('monitoring_interval', 'max_duration', 'screenshot_quality', 'focus_areas', 'alert_keywords')
        }),
        ('Status', {
            'fields': ('status', 'start_time', 'end_time', 'last_screenshot_time')
        }),
        ('Statistics', {
            'fields': ('screenshots_count', 'changes_detected', 'odds_captured', 'errors_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(Screenshot)
class ScreenshotAdmin(admin.ModelAdmin):
    list_display = ('session', 'filename', 'quality', 'file_size_mb', 'odds_detected', 'captured_at')
    list_filter = ('quality', 'page_load_success', 'captured_at')
    search_fields = ('session__site_name', 'filename')
    readonly_fields = ('captured_at', 'file_size_mb')

@admin.register(ChangeDetection)
class ChangeDetectionAdmin(admin.ModelAdmin):
    list_display = ('session', 'change_type', 'severity', 'change_percentage', 'detected_at')
    list_filter = ('change_type', 'severity', 'detected_at')
    search_fields = ('session__site_name', 'description')
    readonly_fields = ('detected_at',)

@admin.register(OddsData)
class OddsDataAdmin(admin.ModelAdmin):
    list_display = ('session', 'odds_type', 'odds_value', 'match_info', 'confidence_score', 'extracted_at')
    list_filter = ('odds_type', 'extracted_at')
    search_fields = ('session__site_name', 'match_info', 'bet_type')
    readonly_fields = ('extracted_at',)

@admin.register(MonitoringAlert)
class MonitoringAlertAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'alert_type', 'priority', 'is_read', 'created_at')
    list_filter = ('alert_type', 'priority', 'is_read', 'is_dismissed', 'created_at')
    search_fields = ('user__email', 'title', 'message')
    readonly_fields = ('created_at', 'read_at')
    
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = "Mark selected alerts as read"
    
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
    mark_as_unread.short_description = "Mark selected alerts as unread"
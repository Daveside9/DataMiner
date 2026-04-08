from django.contrib import admin
from .models import UserAnalytics, SiteAnalytics, DailyStats, PlatformMetrics

@admin.register(UserAnalytics)
class UserAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_sessions', 'total_screenshots', 'total_monitoring_hours', 'last_calculated')
    list_filter = ('last_calculated',)
    search_fields = ('user__email', 'user__full_name')
    readonly_fields = ('last_calculated',)
    
    actions = ['recalculate_analytics']
    
    def recalculate_analytics(self, request, queryset):
        for analytics in queryset:
            analytics.recalculate_stats()
        self.message_user(request, f"Recalculated analytics for {queryset.count()} users.")
    recalculate_analytics.short_description = "Recalculate selected analytics"

@admin.register(SiteAnalytics)
class SiteAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'site_url', 'total_sessions', 'total_users', 'success_rate', 'last_calculated')
    list_filter = ('last_calculated', 'most_used_quality')
    search_fields = ('site_url', 'site_name')
    readonly_fields = ('last_calculated',)
    
    actions = ['recalculate_site_analytics']
    
    def recalculate_site_analytics(self, request, queryset):
        for analytics in queryset:
            analytics.recalculate_stats()
        self.message_user(request, f"Recalculated analytics for {queryset.count()} sites.")
    recalculate_site_analytics.short_description = "Recalculate selected site analytics"

@admin.register(DailyStats)
class DailyStatsAdmin(admin.ModelAdmin):
    list_display = ('date', 'active_users', 'new_users', 'new_sessions', 'total_screenshots')
    list_filter = ('date',)
    date_hierarchy = 'date'
    readonly_fields = ('created_at',)

@admin.register(PlatformMetrics)
class PlatformMetricsAdmin(admin.ModelAdmin):
    list_display = ('total_registered_users', 'active_users_today', 'total_monitoring_sessions', 'last_updated')
    readonly_fields = ('last_updated',)
    
    def has_add_permission(self, request):
        # Only allow one instance
        return not PlatformMetrics.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Don't allow deletion
        return False
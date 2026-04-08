from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'full_name', 'username', 'subscription_plan', 'is_active', 'created_at')
    list_filter = ('subscription_plan', 'is_active', 'is_staff', 'created_at')
    search_fields = ('email', 'full_name', 'username')
    ordering = ('-created_at',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('BetVision Info', {
            'fields': ('full_name', 'subscription_plan', 'avatar', 'bio', 'website', 'location')
        }),
        ('Usage Stats', {
            'fields': ('monitoring_sessions_count', 'total_screenshots', 'total_monitoring_time')
        }),
        ('Preferences', {
            'fields': ('email_notifications', 'default_monitoring_interval', 'preferred_betting_sites')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('BetVision Info', {
            'fields': ('full_name', 'email')
        }),
    )

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'subscription_start_date', 'subscription_end_date', 'dashboard_theme', 'timezone')
    list_filter = ('dashboard_theme', 'timezone', 'auto_renew')
    search_fields = ('user__email', 'user__full_name')
    readonly_fields = ('created_at', 'updated_at')
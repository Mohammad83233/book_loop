from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Genre, UserProfile, Report

# --- This defines the inline model for the User change page ---
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile Information'
    fk_name = 'user'

# --- This is the enhanced CustomUserAdmin ---
class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline, )
    
    # Define the columns you want to see in the user list
    list_display = ('username', 'email', 'get_first_name', 'get_last_name', 'is_active', 'report_count')
    list_select_related = ('userprofile', )

    def get_first_name(self, instance):
        # Get the first_name from the related UserProfile
        return instance.userprofile.first_name
    get_first_name.short_description = 'First Name'

    def get_last_name(self, instance):
        # Get the last_name from the related UserProfile
        return instance.userprofile.last_name
    get_last_name.short_description = 'Last Name'

    def report_count(self, obj):
        return Report.objects.filter(reported_user=obj).count()
    report_count.short_description = 'Reports Received'

    actions = ['block_selected_users', 'unblock_selected_users']

    @admin.action(description='Block selected users')
    def block_selected_users(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f'{queryset.count()} user(s) have been blocked.')

    @admin.action(description='Unblock selected users')
    def unblock_selected_users(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f'{queryset.count()} user(s) have been unblocked.')

# --- Registering your models ---
admin.site.register(Genre)
admin.site.register(Report)

# Unregister the default User admin and register our new custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
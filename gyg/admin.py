from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import (
    User,
    Category,
    Course,
    Course_Include,
    Topic,
    Video,
    File,
    Subscription,
    CouponCode,
    Payment,
    UserCourse,
    UserSubscription,
    Questions,
)


class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password', 'first_name','last_name','is_student','is_teacher','last_login')}),
        ('Permissions', {'fields': (
            'is_active', 
            'is_staff', 
            'is_superuser',
            'groups', 
            'user_permissions',
        )}),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('email', 'password1', 'password2','first_name','last_name','is_student','is_teacher')
            }
        ),
    )

    list_display = ('email', 'first_name', 'last_name', 'is_staff','is_student','is_teacher', 'last_login')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups','is_student','is_teacher')
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)



class Course_IncludeInline(admin.StackedInline):
    model = Course_Include


class TopicInline(admin.StackedInline):
    model = Topic


class VideoInline(admin.StackedInline):
    model = Video

class FileInline(admin.StackedInline):
    model = File


class TopicAdmin(admin.ModelAdmin):
    inlines = [
        VideoInline,
        FileInline,
    ]

class CourseAdmin(admin.ModelAdmin):
    inlines = [
        Course_IncludeInline,
        TopicInline,
    ]


admin.site.register(User, UserAdmin)
admin.site.register(Category)
admin.site.register(Course, CourseAdmin)
admin.site.register(Course_Include)
admin.site.register(Topic, TopicAdmin)
admin.site.register(Video)
admin.site.register(File)
admin.site.register(Subscription)
admin.site.register(CouponCode)
admin.site.register(Payment)
admin.site.register(UserCourse)
admin.site.register(UserSubscription)
admin.site.register(Questions)

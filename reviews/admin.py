from django.contrib import admin
from .models import Review, ReviewHelpful

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['service_name', 'user', 'rating', 'is_verified', 'created_at', 'helpful_count']
    list_filter = ['rating', 'is_verified', 'created_at']
    search_fields = ['service_name', 'user__username', 'title', 'comment']
    readonly_fields = ['created_at', 'updated_at', 'helpful_count']
    
    fieldsets = (
        (None, {
            'fields': ('service_name', 'user', 'rating', 'title', 'comment')
        }),
        ('Metadata', {
            'fields': ('is_verified', 'helpful_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ReviewHelpful)
class ReviewHelpfulAdmin(admin.ModelAdmin):
    list_display = ['review', 'user', 'created_at']
    list_filter = ['created_at']
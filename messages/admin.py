from django.contrib import admin
from .models import (
    Conversation, Message, MessageRead, MessageReport, 
    ConversationParticipant, MessageTemplate
)


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'subject', 'is_active', 'created_at', 'updated_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['subject', 'participants__email']
    readonly_fields = ['id', 'created_at', 'updated_at']
    raw_id_fields = ['booking']
    filter_horizontal = ['participants']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'sender', 'conversation', 'message_type', 'is_read', 
        'is_deleted', 'created_at'
    ]
    list_filter = ['message_type', 'is_read', 'is_deleted', 'created_at']
    search_fields = ['sender__email', 'content', 'conversation__id']
    readonly_fields = ['id', 'created_at', 'updated_at', 'read_at']
    raw_id_fields = ['conversation', 'sender', 'reply_to']
    
    fieldsets = (
        ('Message Details', {
            'fields': ('id', 'conversation', 'sender', 'message_type', 'content')
        }),
        ('Attachments', {
            'fields': ('attachment_url', 'attachment_name', 'attachment_size'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_read', 'is_edited', 'is_deleted')
        }),
        ('Reply', {
            'fields': ('reply_to',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'read_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(MessageReport)
class MessageReportAdmin(admin.ModelAdmin):
    list_display = ['message', 'reporter', 'reason', 'status', 'created_at']
    list_filter = ['reason', 'status', 'created_at']
    search_fields = ['message__id', 'reporter__email', 'description']
    readonly_fields = ['created_at', 'resolved_at']
    raw_id_fields = ['message', 'reporter', 'reviewed_by']
    
    actions = ['mark_reviewed', 'mark_resolved', 'mark_dismissed']
    
    def mark_reviewed(self, request, queryset):
        updated = queryset.update(status='reviewed', reviewed_by=request.user)
        self.message_user(request, f'{updated} reports marked as reviewed.')
    mark_reviewed.short_description = "Mark selected reports as reviewed"
    
    def mark_resolved(self, request, queryset):
        updated = queryset.update(status='resolved', reviewed_by=request.user)
        self.message_user(request, f'{updated} reports marked as resolved.')
    mark_resolved.short_description = "Mark selected reports as resolved"
    
    def mark_dismissed(self, request, queryset):
        updated = queryset.update(status='dismissed', reviewed_by=request.user)
        self.message_user(request, f'{updated} reports dismissed.')
    mark_dismissed.short_description = "Dismiss selected reports"


@admin.register(ConversationParticipant)
class ConversationParticipantAdmin(admin.ModelAdmin):
    list_display = ['conversation', 'user', 'is_muted', 'is_archived', 'joined_at']
    list_filter = ['is_muted', 'is_archived', 'joined_at']
    search_fields = ['conversation__id', 'user__email']
    raw_id_fields = ['conversation', 'user']


@admin.register(MessageTemplate)
class MessageTemplateAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'usage_count', 'is_active', 'for_parents', 'for_caregivers']
    list_filter = ['category', 'is_active', 'for_parents', 'for_caregivers']
    search_fields = ['title', 'content']
    readonly_fields = ['usage_count', 'created_at']


@admin.register(MessageRead)
class MessageReadAdmin(admin.ModelAdmin):
    list_display = ['message', 'user', 'read_at']
    list_filter = ['read_at']
    search_fields = ['message__id', 'user__email']
    raw_id_fields = ['message', 'user']
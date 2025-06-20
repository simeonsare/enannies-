from django.urls import path
from . import views

app_name = 'messages'

urlpatterns = [
    # Conversation management
    path('conversations/', views.ConversationListCreateView.as_view(), name='conversation-list'),
    path('conversations/<uuid:pk>/', views.ConversationDetailView.as_view(), name='conversation-detail'),
    path('conversations/<uuid:conversation_id>/messages/', 
         views.ConversationMessagesView.as_view(), name='conversation-messages'),
    
    # Message management
    path('messages/<uuid:pk>/', views.MessageDetailView.as_view(), name='message-detail'),
    path('conversations/<uuid:conversation_id>/mark-read/', 
         views.MessageMarkReadView.as_view(), name='mark-read'),
    
    # Message actions
    path('messages/<uuid:message_id>/report/', views.MessageReportView.as_view(), name='message-report'),
    
    # Conversation actions
    path('conversations/<uuid:conversation_id>/archive/', 
         views.ConversationArchiveView.as_view(), name='conversation-archive'),
    path('conversations/<uuid:conversation_id>/mute/', 
         views.ConversationMuteView.as_view(), name='conversation-mute'),
    
    # Templates and utilities
    path('templates/', views.MessageTemplateListView.as_view(), name='message-templates'),
    
    # Statistics
    path('stats/', views.conversation_stats, name='conversation-stats'),
    
    # Admin endpoints
    path('admin/reports/', views.AdminMessageReportListView.as_view(), name='admin-report-list'),
    path('admin/reports/<int:pk>/', views.AdminMessageReportDetailView.as_view(), name='admin-report-detail'),
    path('admin/stats/', views.admin_message_stats, name='admin-message-stats'),
]
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .models import Conversation, Message, MessageReport, MessageTemplate, ConversationParticipant
from .serializers import (
    ConversationSerializer, ConversationCreateSerializer, MessageSerializer,
    MessageCreateSerializer, MessageReportSerializer, MessageReportCreateSerializer,
    MessageTemplateSerializer, ConversationStatsSerializer
)

User = get_user_model()


class ConversationListCreateView(generics.ListCreateAPIView):
    """List and create conversations"""
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['is_active']
    ordering = ['-updated_at']
    
    def get_queryset(self):
        return Conversation.objects.filter(
            participants=self.request.user
        ).prefetch_related('participants', 'messages')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ConversationCreateSerializer
        return ConversationSerializer


class ConversationDetailView(generics.RetrieveAPIView):
    """Get conversation details"""
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Conversation.objects.filter(participants=self.request.user)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Mark conversation as read for current user
        participant, created = ConversationParticipant.objects.get_or_create(
            conversation=instance,
            user=request.user
        )
        participant.last_read_at = timezone.now()
        participant.save()
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class ConversationMessagesView(generics.ListCreateAPIView):
    """List and create messages in a conversation"""
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering = ['-created_at']
    
    def get_queryset(self):
        conversation_id = self.kwargs['conversation_id']
        conversation = get_object_or_404(
            Conversation, 
            id=conversation_id, 
            participants=self.request.user
        )
        return Message.objects.filter(
            conversation=conversation,
            is_deleted=False
        ).select_related('sender', 'reply_to')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return MessageCreateSerializer
        return MessageSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        conversation_id = self.kwargs['conversation_id']
        context['conversation'] = get_object_or_404(
            Conversation, 
            id=conversation_id, 
            participants=self.request.user
        )
        return context
    
    def perform_create(self, serializer):
        message = serializer.save()
        
        # Update conversation timestamp
        message.conversation.updated_at = timezone.now()
        message.conversation.save()
        
        # Send notification to other participants
        from notifications.services import NotificationService
        notification_service = NotificationService()
        
        other_participants = message.conversation.participants.exclude(
            id=self.request.user.id
        )
        
        for participant in other_participants:
            notification_service.create_notification(
                recipient=participant,
                notification_type='message_received',
                title=f'New message from {self.request.user.full_name}',
                message=message.content[:100] + '...' if len(message.content) > 100 else message.content,
                action_url=f'/dashboard/messages/{message.conversation.id}/'
            )


class MessageDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update, or delete specific message"""
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Message.objects.filter(
            conversation__participants=self.request.user
        )
    
    def get_object(self):
        obj = super().get_object()
        # Only sender can edit/delete their message
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            if obj.sender != self.request.user:
                raise PermissionError("You can only edit your own messages")
        return obj
    
    def perform_update(self, serializer):
        message = serializer.save(is_edited=True)
        # Update conversation timestamp
        message.conversation.updated_at = timezone.now()
        message.conversation.save()
    
    def perform_destroy(self, instance):
        # Soft delete
        instance.is_deleted = True
        instance.save()


class MessageMarkReadView(APIView):
    """Mark messages as read"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, conversation_id):
        conversation = get_object_or_404(
            Conversation, 
            id=conversation_id, 
            participants=request.user
        )
        
        # Mark all unread messages as read
        unread_messages = Message.objects.filter(
            conversation=conversation,
            is_read=False
        ).exclude(sender=request.user)
        
        updated_count = 0
        for message in unread_messages:
            message.mark_as_read()
            updated_count += 1
        
        # Update participant's last read timestamp
        participant, created = ConversationParticipant.objects.get_or_create(
            conversation=conversation,
            user=request.user
        )
        participant.last_read_at = timezone.now()
        participant.save()
        
        return Response({
            'message': f'{updated_count} messages marked as read'
        })


class MessageReportView(generics.CreateAPIView):
    """Report a message"""
    serializer_class = MessageReportCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        message_id = self.kwargs['message_id']
        context['message'] = get_object_or_404(Message, id=message_id)
        return context
    
    def perform_create(self, serializer):
        message = get_object_or_404(Message, id=self.kwargs['message_id'])
        
        # Check if user already reported this message
        if MessageReport.objects.filter(message=message, reporter=self.request.user).exists():
            raise ValueError("You have already reported this message")
        
        serializer.save()


class MessageTemplateListView(generics.ListAPIView):
    """List message templates"""
    serializer_class = MessageTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category']
    
    def get_queryset(self):
        user = self.request.user
        queryset = MessageTemplate.objects.filter(is_active=True)
        
        # Filter based on user type
        if user.role == 'parent':
            queryset = queryset.filter(for_parents=True)
        elif user.role == 'caregiver':
            queryset = queryset.filter(for_caregivers=True)
        
        return queryset


class ConversationArchiveView(APIView):
    """Archive/unarchive conversation"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, conversation_id):
        conversation = get_object_or_404(
            Conversation, 
            id=conversation_id, 
            participants=request.user
        )
        
        participant, created = ConversationParticipant.objects.get_or_create(
            conversation=conversation,
            user=request.user
        )
        
        action = request.data.get('action', 'archive')
        
        if action == 'archive':
            participant.is_archived = True
            message = 'Conversation archived'
        elif action == 'unarchive':
            participant.is_archived = False
            message = 'Conversation unarchived'
        else:
            return Response(
                {'error': 'Invalid action. Use "archive" or "unarchive"'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        participant.save()
        return Response({'message': message})


class ConversationMuteView(APIView):
    """Mute/unmute conversation"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, conversation_id):
        conversation = get_object_or_404(
            Conversation, 
            id=conversation_id, 
            participants=request.user
        )
        
        participant, created = ConversationParticipant.objects.get_or_create(
            conversation=conversation,
            user=request.user
        )
        
        action = request.data.get('action', 'mute')
        
        if action == 'mute':
            participant.is_muted = True
            message = 'Conversation muted'
        elif action == 'unmute':
            participant.is_muted = False
            message = 'Conversation unmuted'
        else:
            return Response(
                {'error': 'Invalid action. Use "mute" or "unmute"'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        participant.save()
        return Response({'message': message})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def conversation_stats(request):
    """Get conversation statistics for user"""
    user = request.user
    
    conversations = Conversation.objects.filter(participants=user)
    
    # Calculate unread messages
    unread_count = 0
    for conversation in conversations:
        participant = conversation.conversationparticipant_set.filter(user=user).first()
        if participant:
            unread_count += participant.get_unread_count()
    
    stats = {
        'total_conversations': conversations.count(),
        'active_conversations': conversations.filter(is_active=True).count(),
        'total_messages': Message.objects.filter(
            conversation__participants=user
        ).count(),
        'unread_messages': unread_count,
        'messages_today': Message.objects.filter(
            conversation__participants=user,
            created_at__date=timezone.now().date()
        ).count(),
    }
    
    return Response(stats)


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def admin_message_stats(request):
    """Get message statistics for admin dashboard"""
    from datetime import timedelta
    
    now = timezone.now()
    last_30_days = now - timedelta(days=30)
    
    stats = {
        'total_conversations': Conversation.objects.count(),
        'total_messages': Message.objects.count(),
        'messages_last_30_days': Message.objects.filter(
            created_at__gte=last_30_days
        ).count(),
        'active_conversations': Conversation.objects.filter(
            is_active=True,
            updated_at__gte=last_30_days
        ).count(),
        'reported_messages': MessageReport.objects.filter(
            status='pending'
        ).count(),
        'messages_by_type': dict(
            Message.objects.values('message_type').annotate(
                count=Count('id')
            ).values_list('message_type', 'count')
        ),
    }
    
    return Response(stats)


# Admin views for message moderation
class AdminMessageReportListView(generics.ListAPIView):
    """Admin view of message reports"""
    queryset = MessageReport.objects.all()
    serializer_class = MessageReportSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'reason']
    ordering = ['-created_at']


class AdminMessageReportDetailView(generics.RetrieveUpdateAPIView):
    """Admin message report management"""
    queryset = MessageReport.objects.all()
    serializer_class = MessageReportSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def perform_update(self, serializer):
        serializer.save(reviewed_by=self.request.user)
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Conversation, Message, MessageRead, MessageReport, MessageTemplate
from users.serializers import UserSerializer

User = get_user_model()


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    message_type_display = serializers.CharField(source='get_message_type_display', read_only=True)
    reply_to_message = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = [
            'id', 'sender', 'message_type', 'message_type_display', 'content',
            'attachment_url', 'attachment_name', 'attachment_size', 'is_read',
            'is_edited', 'is_deleted', 'reply_to', 'reply_to_message',
            'created_at', 'updated_at', 'read_at'
        ]
        read_only_fields = [
            'id', 'sender', 'is_read', 'is_edited', 'is_deleted',
            'created_at', 'updated_at', 'read_at'
        ]
    
    def get_reply_to_message(self, obj):
        if obj.reply_to:
            return {
                'id': obj.reply_to.id,
                'sender': obj.reply_to.sender.full_name,
                'content': obj.reply_to.content[:100] + '...' if len(obj.reply_to.content) > 100 else obj.reply_to.content,
                'created_at': obj.reply_to.created_at
            }
        return None


class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    other_participant = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'id', 'participants', 'subject', 'is_active', 'booking',
            'last_message', 'unread_count', 'other_participant',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_last_message(self, obj):
        last_message = obj.get_last_message()
        if last_message:
            return MessageSerializer(last_message).data
        return None
    
    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            participant = obj.conversationparticipant_set.filter(user=request.user).first()
            if participant:
                return participant.get_unread_count()
        return 0
    
    def get_other_participant(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            other_participant = obj.get_other_participant(request.user)
            if other_participant:
                return UserSerializer(other_participant).data
        return None


class ConversationCreateSerializer(serializers.ModelSerializer):
    participant_id = serializers.UUIDField(write_only=True)
    initial_message = serializers.CharField(write_only=True)
    booking_id = serializers.UUIDField(write_only=True, required=False)
    
    class Meta:
        model = Conversation
        fields = ['participant_id', 'initial_message', 'subject', 'booking_id']
    
    def validate_participant_id(self, value):
        try:
            participant = User.objects.get(id=value)
            if participant == self.context['request'].user:
                raise serializers.ValidationError("Cannot start conversation with yourself")
        except User.DoesNotExist:
            raise serializers.ValidationError("Participant not found")
        return value
    
    def validate_booking_id(self, value):
        if value:
            from bookings.models import Booking
            try:
                booking = Booking.objects.get(id=value)
                user = self.context['request'].user
                if user not in [booking.parent, booking.caregiver]:
                    raise serializers.ValidationError("You are not part of this booking")
            except Booking.DoesNotExist:
                raise serializers.ValidationError("Booking not found")
        return value
    
    def create(self, validated_data):
        participant_id = validated_data.pop('participant_id')
        initial_message = validated_data.pop('initial_message')
        booking_id = validated_data.pop('booking_id', None)
        
        # Get participants
        current_user = self.context['request'].user
        other_participant = User.objects.get(id=participant_id)
        
        # Check if conversation already exists between these users
        existing_conversation = Conversation.objects.filter(
            participants=current_user
        ).filter(
            participants=other_participant
        ).filter(
            booking_id=booking_id if booking_id else None
        ).first()
        
        if existing_conversation:
            # Add initial message to existing conversation
            Message.objects.create(
                conversation=existing_conversation,
                sender=current_user,
                content=initial_message
            )
            return existing_conversation
        
        # Create new conversation
        conversation = Conversation.objects.create(**validated_data)
        conversation.participants.add(current_user, other_participant)
        
        # Create initial message
        Message.objects.create(
            conversation=conversation,
            sender=current_user,
            content=initial_message
        )
        
        return conversation


class MessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['content', 'message_type', 'attachment_url', 'attachment_name', 'reply_to']
    
    def create(self, validated_data):
        validated_data['sender'] = self.context['request'].user
        validated_data['conversation'] = self.context['conversation']
        return super().create(validated_data)


class MessageReportSerializer(serializers.ModelSerializer):
    reporter = UserSerializer(read_only=True)
    reviewed_by = UserSerializer(read_only=True)
    reason_display = serializers.CharField(source='get_reason_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = MessageReport
        fields = [
            'id', 'reporter', 'reason', 'reason_display', 'description',
            'status', 'status_display', 'reviewed_by', 'resolution_notes',
            'resolved_at', 'created_at'
        ]
        read_only_fields = [
            'id', 'reporter', 'reviewed_by', 'resolution_notes',
            'resolved_at', 'created_at'
        ]


class MessageReportCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageReport
        fields = ['reason', 'description']
    
    def create(self, validated_data):
        validated_data['reporter'] = self.context['request'].user
        validated_data['message'] = self.context['message']
        return super().create(validated_data)


class MessageTemplateSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = MessageTemplate
        fields = [
            'id', 'category', 'category_display', 'title', 'content',
            'usage_count', 'is_active', 'for_parents', 'for_caregivers'
        ]
        read_only_fields = ['id', 'usage_count']


class ConversationStatsSerializer(serializers.Serializer):
    """Serializer for conversation statistics"""
    total_conversations = serializers.IntegerField()
    active_conversations = serializers.IntegerField()
    total_messages = serializers.IntegerField()
    unread_messages = serializers.IntegerField()
    messages_today = serializers.IntegerField()
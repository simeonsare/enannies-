from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class Conversation(models.Model):
    """Conversation between two users"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    participants = models.ManyToManyField(User, related_name='conversations')
    
    # Conversation metadata
    subject = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    
    # Related booking (if conversation is about a specific booking)
    booking = models.ForeignKey(
        'bookings.Booking', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='conversations'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'conversations'
        ordering = ['-updated_at']
    
    def __str__(self):
        participant_names = ', '.join([p.full_name for p in self.participants.all()[:2]])
        return f"Conversation: {participant_names}"
    
    def get_other_participant(self, user):
        """Get the other participant in a 2-person conversation"""
        return self.participants.exclude(id=user.id).first()
    
    def get_last_message(self):
        """Get the most recent message in this conversation"""
        return self.messages.first()
    
    def mark_as_read_for_user(self, user):
        """Mark all messages as read for a specific user"""
        self.messages.filter(sender__ne=user, is_read=False).update(is_read=True)


class Message(models.Model):
    """Individual message within a conversation"""
    
    MESSAGE_TYPES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('file', 'File'),
        ('system', 'System Message'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        Conversation, 
        on_delete=models.CASCADE, 
        related_name='messages'
    )
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    
    # Message content
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES, default='text')
    content = models.TextField()
    
    # File attachments (Supabase Storage URLs)
    attachment_url = models.URLField(blank=True, null=True)
    attachment_name = models.CharField(max_length=255, blank=True)
    attachment_size = models.PositiveIntegerField(blank=True, null=True)  # Size in bytes
    
    # Message status
    is_read = models.BooleanField(default=False)
    is_edited = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    
    
    # Reply functionality
    reply_to = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='replies'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    read_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'messages'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Message from {self.sender.full_name}: {self.content[:50]}..."
    
    def mark_as_read(self):
        """Mark message as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])


class MessageRead(models.Model):
    """Track read status for each user in a conversation"""
    
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='read_receipts')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    read_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'message_reads'
        unique_together = ['message', 'user']
    
    def __str__(self):
        return f"{self.user.full_name} read message {self.message.id}"


class MessageReport(models.Model):
    """Reports for inappropriate messages"""
    
    REPORT_REASONS = [
        ('spam', 'Spam'),
        ('harassment', 'Harassment'),
        ('inappropriate', 'Inappropriate Content'),
        ('scam', 'Scam/Fraud'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('resolved', 'Resolved'),
        ('dismissed', 'Dismissed'),
    ]
    
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='reports')
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='message_reports')
    reason = models.CharField(max_length=20, choices=REPORT_REASONS)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Moderation
    reviewed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='reviewed_message_reports'
    )
    resolution_notes = models.TextField(blank=True)
    resolved_at = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'message_reports'
        unique_together = ['message', 'reporter']
    
    def __str__(self):
        return f"Report by {self.reporter.full_name} - {self.reason}"


class ConversationParticipant(models.Model):
    """Extended information about conversation participants"""
    
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Participant settings
    is_muted = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    
    # Last activity
    last_read_at = models.DateTimeField(blank=True, null=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'conversation_participants'
        unique_together = ['conversation', 'user']
    
    def __str__(self):
        return f"{self.user.full_name} in {self.conversation}"
    
    def get_unread_count(self):
        """Get count of unread messages for this participant"""
        if not self.last_read_at:
            return self.conversation.messages.count()
        
        return self.conversation.messages.filter(
            created_at__gt=self.last_read_at
        ).exclude(sender=self.user).count()


class MessageTemplate(models.Model):
    """Pre-defined message templates for common scenarios"""
    
    TEMPLATE_CATEGORIES = [
        ('booking_inquiry', 'Booking Inquiry'),
        ('booking_confirmation', 'Booking Confirmation'),
        ('schedule_change', 'Schedule Change'),
        ('payment_reminder', 'Payment Reminder'),
        ('thank_you', 'Thank You'),
        ('general', 'General'),
    ]
    
    category = models.CharField(max_length=30, choices=TEMPLATE_CATEGORIES)
    title = models.CharField(max_length=100)
    content = models.TextField()
    
    # Usage tracking
    usage_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    # User type restrictions
    for_parents = models.BooleanField(default=True)
    for_caregivers = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'message_templates'
        ordering = ['category', '-usage_count']
    
    def __str__(self):
        return f"{self.get_category_display()} - {self.title}"
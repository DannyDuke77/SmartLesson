from django.db import models
import uuid
from django.contrib.auth.models import User

# Create your models here.
class Profile(models.Model):
    USER_ROLES = [ 
        ('teacher', 'Teacher'),
        ('ict_officer', 'ICT Officer'),
        ('admin', 'Admin'),
    ]
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        'auth.User', on_delete=models.CASCADE, related_name='profile'
    )
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    tsc_number = models.CharField(max_length=20, blank=True, null=True)
    id_number = models.CharField(max_length=20, blank=True, null=True)

    user_role = models.CharField(
        max_length=50, 
        choices=USER_ROLES, 
        default='teacher'
    )

    def __str__(self):
        return f"{self.user.username}'s Profile"
    
class Notification(models.Model):
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    lesson_plan = models.ForeignKey('lessonplans.LessonPlan', on_delete=models.CASCADE, related_name='notifications', blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message[:50]}"
from .models import Notification

def send_notification(user, message, lesson_plan):
    Notification.objects.create(user=user, message=message, lesson_plan=lesson_plan)

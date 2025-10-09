from django.db import models
from django.contrib.auth.models import User
import uuid
from django.utils.text import slugify

# Create your models here.
class LessonPlan(models.Model):
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    SUBJECT_CHOICES = [
        ('English', 'English'),
        ('Mathematics', 'Mathematics'),
        ('Kiswahili', 'Kiswahili'),
        ('Science', 'Science'),
        ('Social Studies', 'Social Studies'),
        ('CRE', 'CRE'),
        ('Art & Craft', 'Art & Craft'),
        ('PE', 'Physical Education'),
        ('Other', 'Other'),
    ]

    GRADE_LEVELS = [
        ('PP1', 'PP1'),
        ('PP2', 'PP2'),
        ('Grade 1', 'Grade 1'),
        ('Grade 2', 'Grade 2'),
        ('Grade 3', 'Grade 3'),
        ('Grade 4', 'Grade 4'),
        ('Grade 5', 'Grade 5'),
        ('Grade 6', 'Grade 6'),
        ('JSS 7', 'JSS Grade 7'),
        ('JSS 8', 'JSS Grade 8'),
        ('JSS 9', 'JSS Grade 9'),
    ]

    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(unique=True, blank=True, null=True, max_length=255)
    # ---------- Basic Details ----------
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lesson_plans')
    subject = models.CharField(max_length=100, choices=SUBJECT_CHOICES)
    grade_level = models.CharField(max_length=50, choices=GRADE_LEVELS)
    term = models.PositiveIntegerField()
    week = models.PositiveIntegerField()
    topic = models.CharField(max_length=200)
    sub_topic = models.CharField(max_length=200)
    lesson_title = models.CharField(max_length=200)
    lesson_date = models.DateField()

    # ---------- CBC Lesson Components ----------
    general_objective = models.TextField(help_text="Overall goal or aim of the lesson")
    specific_learning_outcomes = models.TextField(help_text="Specific competencies learners should demonstrate")
    key_inquiry_question = models.CharField(max_length=255, blank=True, null=True)
    learning_resources = models.TextField(help_text="Teaching aids, digital tools, and materials to be used")
    introduction = models.TextField(help_text="How the teacher introduces the lesson")
    lesson_development = models.TextField(help_text="Teaching/learning activities, interactions, and differentiation")
    assessment = models.TextField(help_text="How learning outcomes will be assessed")
    reflection = models.TextField(help_text="Teacher's reflection after the lesson", blank=True, null=True)

    # ---------- Supervision & Tracking ----------
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    admin_feedback = models.TextField(blank=True, null=True)
    reviewed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_lessons'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)

    # ---------- Metadata ----------
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.subject} - {self.lesson_title} ({self.teacher.username})"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.grade_level}-{self.subject}-{self.lesson_title}")
            slug = base_slug
            counter = 1
            while LessonPlan.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
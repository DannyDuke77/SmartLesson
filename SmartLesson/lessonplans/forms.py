from django import forms

from .models import LessonPlan

INPUT_CLASSES = (
    "w-full px-3 py-2 rounded-lg border border-gray-300 "
    "focus:outline-none focus:ring-2 focus:ring-blue-500 "
    "focus:border-blue-500 text-gray-700 placeholder-gray-400"
)

class LessonPlanForm(forms.ModelForm):
    class Meta:
        model = LessonPlan
        exclude = ['teacher', 'status', 'admin_feedback', 'reviewed_by', 'created_at', 'updated_at']
        widgets = {
            'lesson_date': forms.DateInput(attrs={'type': 'date', 'class': INPUT_CLASSES}),
            'subject': forms.Select(attrs={'class': INPUT_CLASSES}),
            'grade_level': forms.Select(attrs={'class': INPUT_CLASSES}),
            'term': forms.NumberInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'e.g., 1'}),
            'week': forms.NumberInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'e.g., 3'}),
            'strand': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Main strand area'}),
            'sub_strand': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Sub-strand area'}),
            'lesson_title': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Lesson title'}),

            'general_objective': forms.Textarea(attrs={'class': INPUT_CLASSES, 'rows': 2, 'style': 'resize: none;'}),

            'specific_learning_outcomes': forms.Textarea(attrs={'class': INPUT_CLASSES, 'style': 'resize: none;', 'rows': 4}),

            'key_inquiry_question': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Key question to drive inquiry'}),

            'learning_resources': forms.Textarea(attrs={'class': INPUT_CLASSES, 'style': 'resize: none;', 'rows': 4,}),

            'introduction': forms.Textarea(attrs={'class': INPUT_CLASSES, 'style': 'resize: none;', 'rows': 2}),

            'lesson_development': forms.Textarea(attrs={'class': INPUT_CLASSES, 'style': 'resize: none;', 'rows': 4}),

            'assessment': forms.Textarea(attrs={'class': INPUT_CLASSES, 'style': 'resize: none;', 'rows': 4}),
            
            'reflection': forms.Textarea(attrs={'class': INPUT_CLASSES, 'style': 'resize: none;', 'rows': 2}),
        }

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.models import User

from .models import LessonPlan
from .forms import LessonPlanForm

# Create your views here.
@login_required
def create_lesson_plan(request):
    if request.method == 'POST':
        form = LessonPlanForm(request.POST)
        if form.is_valid():
            lesson_plan = form.save(commit=False)
            lesson_plan.teacher = request.user
            lesson_plan.status = 'submitted'  # You can also use 'draft' if needed
            lesson_plan.save()
            return redirect('lessonplans:lesson_plan_list')
    else:
        form = LessonPlanForm()
    return render(request, 'lessonplans/lesson_plan_form.html', {'form': form})


@login_required
def lesson_plan_list(request):
    user = request.user
    
    # Check user role
    if user.profile.user_role == 'admin' or user.profile.user_role == 'ict_officer':  # Admins and ICT Officers see all plans
        lesson_plans = LessonPlan.objects.all().order_by('-created_at')
    else:
        # Teachers only see their own plans
        lesson_plans = LessonPlan.objects.filter(teacher=user).order_by('-created_at')
        
        # Extra safety: block teachers from admin access via URL trick
        if request.GET.get('from_admin') == 'true':
            messages.error(request, "You do not have permission to access this page.")
            return redirect('core:index')  # redirect to their normal view
    
    paginator = Paginator(lesson_plans, 10)  # 10 plans per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'lessonplans/lesson_plan_list.html', {
        'page_obj': page_obj
    })


@login_required
def lesson_plan_detail(request, slug):
    """
    Displays detailed information for a single lesson plan.
    Teachers see their own plans; admins can view all.
    """
    lesson_plan = get_object_or_404(LessonPlan, slug=slug)

    return render(request, 'lessonplans/lesson_plan_detail.html', {
        'lesson_plan': lesson_plan
    })

@login_required
def edit_lesson_plan(request, slug):
    lesson_plan = get_object_or_404(LessonPlan, slug=slug)

    if lesson_plan.status == 'approved':
        messages.error(request, "Approved lesson plans cannot be edited.")
        return redirect('lessonplans:lesson_plan_detail', slug=slug)

    # Ensure only the owner can edit
    if lesson_plan.teacher != request.user:
        messages.error(request, "You do not have permission to edit this lesson plan.")
        return redirect('lessonplans:lesson_plan_list', slug=slug)

    if request.method == 'POST':
        form = LessonPlanForm(request.POST, instance=lesson_plan)
        if form.is_valid():
            form.save()
            messages.success(request, "Lesson plan updated successfully.")
            return redirect('lessonplans:lesson_plan_detail', slug=slug)
    else:
        form = LessonPlanForm(instance=lesson_plan)

    return render(request, 'lessonplans/lesson_plan_form.html', {'form': form, 'lesson_plan': lesson_plan})

def update_lesson_plan_status(request, slug):
    """
    Updates the status of a lesson plan.
    """
    lesson_plan = get_object_or_404(LessonPlan, slug=slug)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        admin_feedback = request.POST.get('admin_feedback', '').strip()
        if new_status in dict(LessonPlan.STATUS_CHOICES).keys():
            lesson_plan.status = new_status

            lesson_plan.reviewed_by = request.user
            lesson_plan.reviewed_at = timezone.now()
    
                # Save admin feedback if provided
            if admin_feedback:
                lesson_plan.admin_feedback = admin_feedback

            lesson_plan.save(update_fields=['status', 'reviewed_by', 'reviewed_at', 'admin_feedback'])

            messages.success(request, "Lesson plan status updated successfully.")

        return redirect('lessonplans:lesson_plan_detail', slug=lesson_plan.slug)

    return render(request, 'lessonplans/update_status.html', {
        'lesson_plan': lesson_plan,
    })
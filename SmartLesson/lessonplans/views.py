from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models import Q

from .models import LessonPlan
from .forms import LessonPlanForm
from accounts.utils import send_notification
from accounts.models import Profile

# Create your views here.
@login_required
def create_lesson_plan(request):
    if request.method == 'POST':
        form = LessonPlanForm(request.POST)
        if form.is_valid():
            lesson_plan = form.save(commit=False)
            lesson_plan.teacher = request.user
            lesson_plan.status = 'submitted'
            lesson_plan.save()


            admins = Profile.objects.filter(user_role='admin')
            for admin_profile in admins:
                send_notification(
                    admin_profile.user,
                    f"A new lesson plan titled '{lesson_plan.title}' has been submitted by {request.user.get_full_name() or request.user.username}."
                )

            messages.success(request, "Lesson plan created successfully.")
            return redirect('lessonplans:lesson_plan_list')
    else:
        form = LessonPlanForm()
    return render(request, 'lessonplans/lesson_plan_form.html', {'form': form})


@login_required
def lesson_plan_list(request):
    user = request.user
    query = request.GET.get('q', '').strip()

    # Base queryset depending on user role
    if user.profile.user_role in ['admin', 'ict_officer']:
        lesson_plans = LessonPlan.objects.all().order_by('-created_at')
    else:
        lesson_plans = LessonPlan.objects.filter(teacher=user).order_by('-created_at')

        # Extra safety: block teachers from forced admin view
        if request.GET.get('from_admin') == 'true':
            messages.error(request, "You do not have permission to access this page.")
            return redirect('core:index')

    if query:
        lesson_plans = lesson_plans.filter(
            Q(lesson_title__icontains=query) |
            Q(subject__icontains=query) |
            Q(grade_level__icontains=query) |
            Q(status__icontains=query)
        )

    # Pagination
    paginator = Paginator(lesson_plans, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'lessonplans/lesson_plan_list.html', {
        'page_obj': page_obj,
        'query': query,
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

            if lesson_plan.status == 'rejected':
                # reset status
                lesson_plan.status = 'submitted'
                lesson_plan.save(update_fields=['status'])

                # Notify admins
                admins = Profile.objects.filter(user_role='admin')
                for admin_profile in admins:
                    send_notification(
                        admin_profile.user,
                        f"The lesson plan '{lesson_plan.lesson_title}' has been updated and resubmitted by {request.user.get_full_name() or request.user.username}.",
                        lesson_plan
                    )

            messages.success(request, "Lesson plan updated successfully.")
            return redirect('lessonplans:lesson_plan_detail', slug=lesson_plan.slug)
    else:
        form = LessonPlanForm(instance=lesson_plan)

    return render(request, 'lessonplans/lesson_plan_form.html', {'form': form, 'lesson_plan': lesson_plan,})

@login_required
def update_lesson_plan_status(request, slug):
    lesson_plan = get_object_or_404(LessonPlan, slug=slug)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        admin_feedback = request.POST.get('admin_feedback', '').strip()

        if new_status == 'rejected' and not admin_feedback:
            messages.error(request, "Please provide feedback when rejecting a lesson plan.")
            return redirect('lessonplans:update_lesson_plan_status', slug=lesson_plan.slug)

        if lesson_plan.status == 'approved':
            messages.error(request, "Approved lesson plans cannot be modified.")
            return redirect('lessonplans:lesson_plan_detail', slug=lesson_plan.slug)

        if new_status in dict(LessonPlan.STATUS_CHOICES).keys():
            lesson_plan.status = new_status
            lesson_plan.reviewed_by = request.user
            lesson_plan.reviewed_at = timezone.now()
            lesson_plan.admin_feedback = admin_feedback
            lesson_plan.save()

            # Notify the teacher
            message = f"Your lesson plan '{lesson_plan.lesson_title}' has been {new_status} by {request.user.get_full_name() or request.user.username}."
            send_notification(lesson_plan.teacher, message, lesson_plan)

            messages.success(request, "Lesson plan status updated successfully.")
            return redirect('lessonplans:lesson_plan_detail', slug=lesson_plan.slug)

    return render(request, 'lessonplans/update_status.html', {
        'lesson_plan': lesson_plan,
    })

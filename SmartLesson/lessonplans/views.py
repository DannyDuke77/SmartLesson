from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

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
    return render(request, 'lessonplans/create_lesson_plan.html', {'form': form})


@login_required
def lesson_plan_list(request):
    if request.user.profile.user_role == 'admin' or request.user.profile.user_role == 'ict_officer':
        lesson_plans = LessonPlan.objects.all().order_by('-created_at')
    else:
        lesson_plans = LessonPlan.objects.filter(teacher=request.user).order_by('-created_at')
    
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
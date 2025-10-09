from django.shortcuts import render

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator

from lessonplans.models import LessonPlan

# Create your views here.
def index(request):
    return render(request, 'core/index.html')

@login_required
def dashboard(request):
    user = request.user
    role = user.profile.user_role

    if role in ['admin', 'ict_officer']:
        lesson_plans = LessonPlan.objects.all().order_by('-created_at')
        total_users = User.objects.count()
        teachers_count = User.objects.filter(profile__user_role='teacher').count()
        admins_count = User.objects.filter(profile__user_role='admin').count()
        ict_count = User.objects.filter(profile__user_role='ict_officer').count()
    else:
        lesson_plans = LessonPlan.objects.filter(teacher=user).order_by('-created_at')
        total_users = teachers_count = admins_count = ict_count = None

    # Stats
    total_plans = lesson_plans.count()
    approved_count = lesson_plans.filter(status='approved').count()
    rejected_count = lesson_plans.filter(status='rejected').count()
    pending_count = lesson_plans.filter(status='pending').count()

    # Pagination
    paginator = Paginator(lesson_plans, 10)  # 10 lesson plans per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'role': role,
        'total_plans': total_plans,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'pending_count': pending_count,
        'page_obj': page_obj,
        'total_users': total_users,
        'teachers_count': teachers_count,
        'admins_count': admins_count,
        'ict_count': ict_count,
    }
    return render(request, 'core/dashboard.html', context)
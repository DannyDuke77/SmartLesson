from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models import Q
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import inch
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from openpyxl import Workbook
import datetime
from openpyxl.styles import PatternFill, Font, Alignment

from .models import LessonPlan
from .forms import LessonPlanForm
from accounts.utils import send_notification
from accounts.models import Profile
from accounts.decorators import role_required

# Create your views here.
@role_required('teacher')
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


@role_required('teacher', 'admin', 'ict_officer')
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

@role_required('teacher', 'admin', 'ict_officer')
def lesson_plan_detail(request, slug):
    """
    Displays detailed information for a single lesson plan.
    Teachers see their own plans; admins can view all.
    """
    lesson_plan = get_object_or_404(LessonPlan, slug=slug)

    return render(request, 'lessonplans/lesson_plan_detail.html', {
        'lesson_plan': lesson_plan
    })

@role_required('teacher')
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

@role_required('admin', 'ict_officer')
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

@role_required('admin', 'ict_officer')
def coverage_reports(request):
    if request.user.profile.user_role not in ['admin', 'ict_officer']:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('core:index')
    
    plans = LessonPlan.objects.all().select_related('teacher', 'reviewed_by')

    # Filtering
    teacher = request.GET.get('teacher')
    subject = request.GET.get('subject')
    term = request.GET.get('term')
    status = request.GET.get('status')
    grade_level = request.GET.get('grade_level')


    if teacher:
        plans = plans.filter(teacher__username__icontains=teacher)
    if subject:
        plans = plans.filter(subject=subject)
    if term:
        plans = plans.filter(term=term)
    if status:
        plans = plans.filter(status=status)
    if grade_level:
        plans = plans.filter(grade_level=grade_level)

    # Stats
    total = plans.count()
    approved = plans.filter(status='approved').count()
    pending = plans.filter(status='submitted').count()
    rejected = plans.filter(status='rejected').count()
    coverage = int((approved / total) * 100) if total else 0

    stats = {
        'total': total,
        'approved': approved,
        'pending': pending,
        'rejected': rejected,
        'coverage': coverage,
    }

    # Pagination
    paginator = Paginator(plans, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'lessonplans/coverage_reports.html', {
        'lesson_plans': plans,
        'page_obj': page_obj,
        'stats': stats,
        'subject_choices': dict(LessonPlan.SUBJECT_CHOICES),
        'status_choices': dict(LessonPlan.STATUS_CHOICES),
        'grade_levels': dict(LessonPlan.GRADE_LEVELS),
    })


@role_required('teacher', 'admin', 'ict_officer')
def download_lesson_plan_pdf(request, slug):
    
    lesson_plan = get_object_or_404(LessonPlan, slug=slug)

    user_role = getattr(request.user.profile, 'user_role', None)
    if not (user_role in ['admin', 'ict_officer'] or request.user == lesson_plan.teacher):
        messages.error(request, "You don't have permission to download this lesson plan.")
        return redirect('lessonplans:lesson_plan_detail', slug=lesson_plan.slug)

    # ---- HTTP Response ----
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{lesson_plan.lesson_title}.pdf"'

    # ---- PDF Setup ----
    doc = SimpleDocTemplate(response, pagesize=A4,
                            rightMargin=40, leftMargin=40,
                            topMargin=60, bottomMargin=50)
    story = []
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'],
                                 fontSize=18, spaceAfter=12, textColor=colors.HexColor("#1E40AF"))
    section_title = ParagraphStyle('SectionTitle', parent=styles['Heading2'],
                                   fontSize=14, textColor=colors.HexColor("#2563EB"),
                                   spaceBefore=12, spaceAfter=6)
    normal = ParagraphStyle('Normal', parent=styles['Normal'], fontSize=11, leading=16)
    small = ParagraphStyle('Small', parent=styles['Normal'], fontSize=9, textColor=colors.grey)

    # ---- Header ----
    story.append(Paragraph("<b>SmartLesson Planner</b>", title_style))
    story.append(Paragraph("Official CBC Lesson Plan Document", small))
    story.append(Spacer(1, 0.3 * inch))

    # ---- Basic Info Table ----
    data = [
        ['Lesson Title:', lesson_plan.lesson_title],
        ['Subject:', lesson_plan.subject],
        ['Grade Level:', lesson_plan.grade_level],
        ['Term:', lesson_plan.term],
        ['Week:', lesson_plan.week],
        ['Lesson Date:', lesson_plan.lesson_date.strftime('%Y-%m-%d')],
        ['Teacher:', lesson_plan.teacher.get_full_name() or lesson_plan.teacher.username],
        ['Status:', lesson_plan.get_status_display()],
    ]
    table = Table(data, hAlign='LEFT', colWidths=[120, 360])
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor("#1E3A8A")),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.2 * inch))

    # ---- CBC Components ----
    sections = [
        ("Strand", lesson_plan.strand),
        ("Sub-strand", lesson_plan.sub_strand),
        ("General Objective", lesson_plan.general_objective),
        ("Specific Learning Outcomes", lesson_plan.specific_learning_outcomes),
        ("Key Inquiry Question", lesson_plan.key_inquiry_question or "—"),
        ("Learning Resources", lesson_plan.learning_resources),
        ("Introduction", lesson_plan.introduction),
        ("Lesson Development", lesson_plan.lesson_development),
        ("Assessment", lesson_plan.assessment),
        ("Reflection", lesson_plan.reflection or "—"),
        ("Admin Feedback", lesson_plan.admin_feedback or "—"),
    ]

    for title, content in sections:
        story.append(Paragraph(title, section_title))
        story.append(Paragraph(content.replace("\n", "<br/>"), normal))
        story.append(Spacer(1, 0.15 * inch))

    # ---- Review Info ----
    story.append(Paragraph("Supervision & Tracking", section_title))
    story.append(Paragraph(f"Reviewed by: {lesson_plan.reviewed_by.get_full_name() if lesson_plan.reviewed_by else '—'}", normal))
    story.append(Paragraph(f"Reviewed at: {lesson_plan.reviewed_at.strftime('%Y-%m-%d %H:%M') if lesson_plan.reviewed_at else '—'}", normal))
    story.append(Spacer(1, 0.3 * inch))

    # ---- Footer ----
    story.append(Paragraph(f"Generated on: {timezone.now().strftime('%Y-%m-%d %H:%M')}", small))
    story.append(Paragraph("SmartLesson Planner © 2025", small))

    # ---- Build Document ----
    doc.build(story)

    return response

@role_required('admin', 'ict_officer')
def export_coverage_pdf(request):
    plans = LessonPlan.objects.select_related('teacher', 'reviewed_by').all()

    if request.user.profile.user_role not in ['admin', 'ict_officer']:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('core:index')

    response = HttpResponse(content_type='application/pdf')
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H.%M")
    response['Content-Disposition'] = f'attachment; filename="coverage_report_{timestamp}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=landscape(A4))
    elements = []

    styles = getSampleStyleSheet()
    title = Paragraph("<b>SmartLesson Planner - Coverage Report</b>", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))

    data = [["Teacher", "Subject", "Grade", "Term", "Week", "Status", "Reviewed By", "Reviewed At"]]

    for plan in plans:
        data.append([
            plan.teacher.get_full_name() or plan.teacher.username,
            plan.get_subject_display(),
            plan.grade_level,
            plan.term,
            plan.week,
            plan.status.title(),
            plan.reviewed_by.get_full_name() if plan.reviewed_by else "—",
            plan.reviewed_at.strftime('%Y-%m-%d') if plan.reviewed_at else "—",
        ])

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2563eb")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
    ]))

    elements.append(table)
    doc.build(elements)
    return response

@role_required('admin', 'ict_officer')
def export_coverage_excel(request):
    plans = LessonPlan.objects.select_related('teacher', 'reviewed_by').all()

    if request.user.profile.user_role not in ['admin', 'ict_officer']:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('core:index')

    wb = Workbook()
    ws = wb.active
    ws.title = "Coverage Report"

    headers = ["Teacher", "Subject", "Grade", "Term", "Week", "Status", "Reviewed By", "Reviewed At"]
    ws.append(headers)

    for plan in plans:
        ws.append([
            plan.teacher.get_full_name() or plan.teacher.username,
            plan.get_subject_display(),
            plan.grade_level,
            plan.term,
            plan.week,
            plan.status.title(),
            plan.reviewed_by.get_full_name() if plan.reviewed_by else "—",
            plan.reviewed_at.strftime('%Y-%m-%d') if plan.reviewed_at else "—",
        ])

    # Style headers
    header_fill = PatternFill(start_color="2563EB", end_color="2563EB", fill_type="solid")
    header_font = Font(color="FFFFFF", bold=True)
    center_align = Alignment(horizontal="center", vertical="center")

    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = center_align

    for column_cells in ws.columns:
        length = max(len(str(cell.value or "")) for cell in column_cells)
        adjusted_width = length + 4
        ws.column_dimensions[column_cells[0].column_letter].width = adjusted_width

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H.%M")
    response['Content-Disposition'] = f'attachment; filename="coverage_report_{timestamp}.xlsx"'
    wb.save(response)
    return response

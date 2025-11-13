from django.urls import path

from . import views

app_name = 'lessonplans'

urlpatterns = [
    path('create/', views.create_lesson_plan, name='create_lesson_plan'),
    path('edit/<slug:slug>/', views.edit_lesson_plan, name='edit_lesson_plan'),
    path('my-plans/', views.my_lesson_plans, name='my_lesson_plans'),
    path('review-plans/', views.review_lesson_plans, name='review_lesson_plans'),
    path('detail/<slug:slug>/', views.lesson_plan_detail, name='lesson_plan_detail'),
    path('update-status/<slug:slug>/', views.update_lesson_plan_status, name='update_lesson_plan_status'),
    path('download/<slug:slug>/', views.download_lesson_plan_pdf, name='download_lesson_plan_pdf'),
    path('coverage-reports/', views.coverage_reports, name='coverage_reports'),
    path('coverage-reports/export/pdf/', views.export_coverage_pdf, name='export_pdf'),
    path('coverage-reports/export/excel/', views.export_coverage_excel, name='export_excel'),
]
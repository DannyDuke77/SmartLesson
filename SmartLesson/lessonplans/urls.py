from django.urls import path

from . import views

app_name = 'lessonplans'

urlpatterns = [
    path('create/', views.create_lesson_plan, name='create_lesson_plan'),
    path('list/', views.lesson_plan_list, name='lesson_plan_list'),
    path('detail/<slug:slug>/', views.lesson_plan_detail, name='lesson_plan_detail'),
]
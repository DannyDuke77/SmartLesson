from django.urls import path
from django.contrib.auth import views as auth_views

from . import views
from .forms import CustomPasswordChangeForm

app_name = 'accounts'

urlpatterns = [
    path('create-user/', views.create_user, name='create_user'),
    path('edit/<uuid:user_uuid>/', views.edit_user, name='edit_user'),

    # Login paths for different roles
    path('login/teacher/', views.login_view, {'role': 'teacher'}, name='teacher_login'),
    path('login/admin/', views.login_view, {'role': 'admin'}, name='admin_login'),
    path('login/ict_officer/', views.login_view, {'role': 'ict_officer'}, name='ict_officer_login'),
    
    path('logout/', views.logout_view, name='logout'),
    path('manage/', views.manage_users, name='manage_users'),
    path('profile/', views.profile_view, name='profile'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/<int:pk>/read/', views.mark_notification_read, name='mark_notification_read'),

    path('password/change/', 
         auth_views.PasswordChangeView.as_view(
             form_class=CustomPasswordChangeForm,
             template_name='accounts/password_change.html',
             success_url='/accounts/password/change/done/'
         ), 
         name='password_change'),

    path('password/change/done/', 
         auth_views.PasswordChangeDoneView.as_view(
             template_name='accounts/password_change_done.html'
         ), 
         name='password_change_done'),

    path('fetch-notifications/', views.fetch_notifications, name='fetch_notifications'),

]
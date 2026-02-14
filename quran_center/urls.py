from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.welcome_view, name='welcome'),
    path('register/', views.home, name='home'),
    path('parent-inquiry/', views.parent_inquiry, name='parent_inquiry'),
    path('success/', views.success_view, name='success'),
    path('pending/', views.pending_students, name='pending_students'),
    path('attendance/', views.take_attendance, name='take_attendance'),
    path('attendance/update/', views.update_attendance, name='update_attendance'),
    path('attendance/success/', views.attendance_success_view, name='attendance_success'),
    path('teacher-dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('nominate-exam/', views.nominate_for_exam, name='nominate_exam'),
    path('teacher-nominations/', views.teacher_nominations, name='teacher_nominations'),
    path('teacher-nominations/<int:nomination_id>/delete/', views.delete_nomination, name='delete_nomination'),
    path('nominated-students/', views.nominated_students, name='nominated_students'),
    path('pending/<int:student_id>/delete/', views.delete_pending_student, name='delete_pending_student'),
    path('association-candidates/', views.association_candidates, name='association_candidates'),
    path('association-results/', views.association_results, name='association_results'),
    path('preparer-attendance/', views.preparer_attendance_summary, name='preparer_attendance_summary'),
    path('preparer-attendance/take/', views.preparer_take_attendance, name='preparer_take_attendance'),
    path('preparer-absent-contacts/', views.preparer_absent_contacts, name='preparer_absent_contacts'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
]
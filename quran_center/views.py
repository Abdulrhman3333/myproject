from django.shortcuts import render, redirect, get_object_or_404
from .forms import StudentRegistrationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Student, Attendance
from django.utils import timezone

def home(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('success')
    else:
        form = StudentRegistrationForm()
    
    return render(request, 'home.html', {'form': form})

@login_required
def pending_students(request):
    # جلب الطلاب الذين حالتهم "منتظر" فقط
    students = Student.objects.filter(status='منتظر')
    
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        student = get_object_or_404(Student, id=student_id)
        student.status = 'منتظم'
        student.save()
        return redirect('pending_students')

    return render(request, 'pending.html', {'students': students})

@login_required
def take_attendance(request):
    # جلب طلاب هذا المعلم فقط والذين حالتهم "منتظم"
    students = Student.objects.filter(teacher=request.user, status='منتظم')
    
    if request.method == 'POST':
        for student in students:
            status = request.POST.get(f'status_{student.id}')
            if status:
                Attendance.objects.update_or_create(
                    student=student,
                    date=timezone.now().date(),
                    defaults={'status': status}
                )
        return redirect('attendance_success')

    return render(request, 'attendance.html', {'students': students})

def success_view(request):
    return render(request, 'success.html')

def attendance_success_view(request):
    return render(request, 'attendance_success.html')

# 1. للمدير فقط: لا يدخل إلا من لديه صلاحيات Superuser
def is_admin(user):
    return user.is_superuser

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    # كود لوحة التحكم الشاملة
    return render(request, 'admin_view.html')

# 2. للمعلمين: أي مستخدم مسجل دخول (معلم أو مدير)
@login_required
def attendance_view(request):
    # كود التحضير
    return render(request, 'attendance.html')
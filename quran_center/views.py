from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .forms import StudentRegistrationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Student, Attendance, StageSupervisor, AcademicCalendar, ExamNomination, UserRole
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models import Count, Q, Max
from datetime import datetime

# دالة مساعدة للتحقق من صلاحية مشرف المرحلة
def is_stage_supervisor(user):
    """تحقق إذا كان المستخدم مشرف مرحلة"""
    return hasattr(user, 'stage_supervisor') or user.is_superuser or user_has_role(user, 'supervisor')


def user_has_role(user, role_code):
    """تحقق من العضوية"""
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return UserRole.objects.filter(user=user, role__code=role_code).exists()

@login_required
def pending_students(request):
    """صفحة الطلاب المنتظرين - للمشرفين فقط"""
    # التحقق من الصلاحيات
    if not is_stage_supervisor(request.user):
        return redirect('home')
    
    # جلب الطلاب حسب مرحلة المشرف
    if request.user.is_superuser or user_has_role(request.user, 'supervisor'):
        # المدير أو المشرف العام يرى جميع الطلاب
        students = Student.objects.filter(status='منتظر')
    else:
        # المشرف يرى فقط طلاب مرحلته
        supervisor = request.user.stage_supervisor
        students = Student.objects.filter(status='منتظر', educational_stage=supervisor.stage)
    
    # جلب جميع المعلمين لقائمة التعيين (المعلمين الحاليين + الموظفين)
    teachers = User.objects.filter(
        Q(student__isnull=False) | Q(is_staff=True)
    ).distinct().order_by('username')
    
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        teacher_id = request.POST.get('teacher_id')
        student = get_object_or_404(Student, id=student_id)
        
        # تعيين المعلم إذا تم اختياره
        if teacher_id:
            teacher = get_object_or_404(User, id=teacher_id)
            student.teacher = teacher
        
        student.status = 'منتظم'
        student.save()
        return redirect('pending_students')

    return render(request, 'pending.html', {'students': students, 'teachers': teachers})

@login_required
def take_attendance(request):
    """التحضير اليومي للمعلم"""
    # جلب طلاب هذا المعلم فقط والذين حالتهم "منتظم"
    students = Student.objects.filter(teacher=request.user, status='منتظم')
    
    # الحصول على التاريخ الحالي
    today = timezone.now().date()

    selected_date_str = request.POST.get('attendance_date') or request.GET.get('date') or str(today)
    try:
        selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
    except ValueError:
        selected_date = today
    
    # تحديد اليوم بالعربي
    weekday_map = {
        6: 'الأحد',      # Sunday
        0: 'الاثنين',    # Monday
        1: 'الثلاثاء',   # Tuesday
        2: 'الأربعاء',   # Wednesday
        3: 'الخميس',    # Thursday
    }
    current_weekday = weekday_map.get(selected_date.weekday(), 'الأحد')
    
    # الحصول على رقم الأسبوع من التقويم
    current_week = AcademicCalendar.get_week_from_date(selected_date)
    
    if request.method == 'POST':
        posted_date_str = request.POST.get('attendance_date', str(selected_date))
        try:
            posted_date = datetime.strptime(posted_date_str, "%Y-%m-%d").date()
        except ValueError:
            posted_date = selected_date

        selected_weekday = weekday_map.get(posted_date.weekday(), 'الأحد')
        selected_week = AcademicCalendar.get_week_from_date(posted_date)
        
        for student in students:
            status = request.POST.get(f'status_{student.id}')
            if status:
                Attendance.objects.update_or_create(
                    student=student,
                    date=posted_date,
                    defaults={
                        'status': status,
                        'weekday': selected_weekday,
                        'week_number': selected_week
                    }
                )
        return redirect('attendance_success')

    existing_attendance = Attendance.objects.filter(student__in=students, date=selected_date)
    attendance_map = {item.student_id: item.status for item in existing_attendance}
    
    context = {
        'students': students,
        'current_weekday': current_weekday,
        'current_week': current_week,
        'selected_date': selected_date,
        'today': today,
        'attendance_map': attendance_map,
    }
    
    return render(request, 'attendance.html', context)

def success_view(request):
    return render(request, 'success.html')

def attendance_success_view(request):
    return render(request, 'attendance_success.html')

# دالة للتحقق من أن المستخدم ليس معلماً أو مشرفاً (للصفحة العامة فقط)
def home(request):
    """الصفحة الرئيسية - نموذج التسجيل العام"""
    # السماح للمشرفين والمدير بالوصول لصفحة التسجيل
    if request.user.is_authenticated:
        # المدير والمشرفون يمكنهم الوصول
        if not (is_stage_supervisor(request.user) or request.user.is_superuser):
            # المعلمون العاديون يتم توجيههم
            if Student.objects.filter(teacher=request.user).exists():
                return redirect('teacher_dashboard')
            elif request.user.is_staff:
                return redirect('admin:index')
    
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('success')
    else:
        form = StudentRegistrationForm()
    
    return render(request, 'home.html', {'form': form})

@login_required
def teacher_dashboard(request):
    """لوحة تحكم المعلم - عرض الإحصائيات"""
    # جلب طلاب المعلم
    students = Student.objects.filter(teacher=request.user, status='منتظم')
    
    # إحصائيات عامة
    total_students = students.count()
    
    attendance_stats = {}
    for student in students:
        attendances = Attendance.objects.filter(
            student=student
        )
        
        total_days = attendances.count()
        present = attendances.filter(status='حاضر').count()
        absent = attendances.filter(status='غائب').count()
        excused = attendances.filter(status='مستأذن').count()
        
        attendance_stats[student.id] = {
            'student': student,
            'total_days': total_days,
            'present': present,
            'absent': absent,
            'excused': excused,
            'absent_days': list(attendances.filter(status='غائب').values_list('date', flat=True))
        }
    
    context = {
        'total_students': total_students,
        'attendance_stats': attendance_stats,
    }
    
    return render(request, 'teacher_dashboard.html', context)

@login_required
def nominate_for_exam(request):
    """صفحة ترشيح الطلاب للاختبار الداخلي"""
    # جلب طلاب المعلم
    students = Student.objects.filter(teacher=request.user, status='منتظم')
    
    if request.method == 'POST':
        for student in students:
            teacher_grade = request.POST.get(f'teacher_grade_{student.id}')
            if teacher_grade:
                ExamNomination.objects.create(
                    student=student,
                    teacher=request.user,
                    last_tested_part=student.last_tested_part,
                    teacher_grade=teacher_grade
                )
        return redirect('teacher_dashboard')
    
    return render(request, 'nominate_exam.html', {'students': students})

@login_required
def nominated_students(request):
    """صفحة المرشحين للاختبار"""
    if not user_has_role(request.user, 'examiner'):
        return redirect('home')

    nominations = ExamNomination.objects.filter(internal_passed=False)
    
    if request.method == 'POST':
        for nomination in nominations:
            internal_grade = request.POST.get(f'internal_grade_{nomination.id}')
            if internal_grade:
                nomination.internal_grade = internal_grade
                teacher_ok = nomination.teacher_grade is not None and float(nomination.teacher_grade) >= 85
                internal_ok = float(internal_grade) >= 85
                nomination.internal_passed = teacher_ok and internal_ok
                nomination.save()
        return redirect('nominated_students')
    
    # إضافة الجزء التالي لكل ترشيح
    nominations_with_next = []
    for nomination in nominations:
        nominations_with_next.append({
            'nomination': nomination,
            'next_part': nomination.get_next_part()
        })
    
    return render(request, 'nominated_students.html', {'nominations': nominations_with_next})


@login_required
def association_candidates(request):
    """مرشحو اختبار الجمعية"""
    if not user_has_role(request.user, 'examiner'):
        return redirect('home')

    nominations = ExamNomination.objects.filter(internal_passed=True, association_tested=False)

    if request.method == 'POST':
        for nomination in nominations:
            association_grade = request.POST.get(f'association_grade_{nomination.id}')
            if association_grade:
                nomination.association_grade = association_grade
                nomination.association_tested = True
                nomination.save()
        return redirect('association_candidates')

    nominations_with_next = []
    for nomination in nominations:
        nominations_with_next.append({
            'nomination': nomination,
            'next_part': nomination.get_next_part()
        })

    return render(request, 'association_candidates.html', {'nominations': nominations_with_next})


@login_required
def association_results(request):
    """نتائج اختبار الجمعية"""
    if not (user_has_role(request.user, 'examiner') or user_has_role(request.user, 'manager')):
        return redirect('home')

    nominations = ExamNomination.objects.filter(association_tested=True)
    return render(request, 'association_results.html', {'nominations': nominations})


@login_required
def preparer_attendance_summary(request):
    """متابعة تحضير المعلمين لليوم"""
    if not user_has_role(request.user, 'preparer'):
        return redirect('home')

    target_date = timezone.now().date()
    teachers = User.objects.filter(student__isnull=False).distinct().order_by('username')
    completed = []

    for teacher in teachers:
        student_count = Student.objects.filter(teacher=teacher, status='منتظم').count()
        if student_count == 0:
            continue
        attendance_qs = Attendance.objects.filter(student__teacher=teacher, date=target_date)
        if attendance_qs.count() >= student_count:
            last_time = attendance_qs.aggregate(last_time=Max('created_at'))['last_time']
            completed.append({
                'teacher': teacher,
                'student_count': student_count,
                'last_time': last_time,
            })

    context = {
        'target_date': target_date,
        'completed': completed,
    }
    return render(request, 'preparer_attendance_summary.html', context)


@login_required
def preparer_absent_contacts(request):
    """أرقام أولياء الأمور للغائبين وإحصائية الغياب"""
    if not user_has_role(request.user, 'preparer'):
        return redirect('home')

    target_date_str = request.GET.get('date') or str(timezone.now().date())
    try:
        target_date = datetime.strptime(target_date_str, "%Y-%m-%d").date()
    except ValueError:
        target_date = timezone.now().date()

    if request.method == 'POST':
        reset_student_id = request.POST.get('reset_student_id')
        if reset_student_id:
            student = get_object_or_404(Student, id=reset_student_id)
            student.absence_reset_at = timezone.now().date()
            student.save()
            return redirect(f"{reverse('preparer_absent_contacts')}?date={target_date}")

    absences = Attendance.objects.filter(date=target_date, status='غائب')
    phones = []
    for attendance in absences.select_related('student'):
        phone = attendance.student.parent_phone or ''
        digits = ''.join([ch for ch in phone if ch.isdigit()])
        if digits.startswith('966'):
            formatted = digits
        elif digits.startswith('0'):
            formatted = '966' + digits[1:]
        elif digits.startswith('5'):
            formatted = '966' + digits
        else:
            formatted = digits
        if formatted:
            phones.append(formatted)

    phones_text = "\n".join(sorted(set(phones)))

    at_risk = []
    students = Student.objects.filter(status='منتظم')
    for student in students:
        if student.absence_reset_at:
            temp_count = Attendance.objects.filter(
                student=student,
                status='غائب',
                date__gt=student.absence_reset_at
            ).count()
        else:
            temp_count = Attendance.objects.filter(
                student=student,
                status='غائب'
            ).count()
        if temp_count >= 5:
            at_risk.append({
                'student': student,
                'temp_count': temp_count,
            })

    context = {
        'target_date': target_date,
        'phones_text': phones_text,
        'phones_count': len(set(phones)),
        'at_risk': at_risk,
    }
    return render(request, 'preparer_absent_contacts.html', context)

# 1. للمدير فقط: لا يدخل إلا من لديه صلاحيات Superuser
def is_admin(user):
    return user.is_superuser or user_has_role(user, 'manager')

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
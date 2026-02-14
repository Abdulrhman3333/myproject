from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .forms import StudentRegistrationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Student, Attendance, TeacherAttendance, StageSupervisor, AcademicCalendar, ExamNomination, UserRole
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
    if request.user.is_superuser:
        # المدير يرى جميع الطلاب
        students = Student.objects.filter(status='منتظر')
    elif hasattr(request.user, 'stage_supervisor'):
        # مشرف المرحلة يرى فقط طلاب مرحلته
        supervisor = request.user.stage_supervisor
        students = Student.objects.filter(status='منتظر', educational_stage=supervisor.stage)
    elif user_has_role(request.user, 'supervisor'):
        # المشرف العام يرى جميع الطلاب
        students = Student.objects.filter(status='منتظر')
    else:
        students = Student.objects.none()
    
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
    
    success = False
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
        # بدل redirect، نعيد تحميل البيانات وإظهار رسالة نجاح
        success = True
        selected_date = posted_date
        current_weekday = selected_weekday
        current_week = selected_week

    existing_attendance = Attendance.objects.filter(student__in=students, date=selected_date)
    attendance_map = {item.student_id: item.status for item in existing_attendance}
    
    # إضافة حالة لكل طالب (حاضر افتراضياً إذا لم يكن له سجل)
    students_with_status = []
    for student in students:
        status = attendance_map.get(student.id, 'حاضر')
        students_with_status.append({
            'student': student,
            'status': status
        })
    
    context = {
        'students_with_status': students_with_status,
        'current_weekday': current_weekday,
        'current_week': current_week,
        'selected_date': selected_date,
        'today': today,
        'attendance_map': attendance_map,
        'success': success,
    }
    
    return render(request, 'attendance.html', context)

def success_view(request):
    return render(request, 'success.html')

def attendance_success_view(request):
    return render(request, 'attendance_success.html')

def welcome_view(request):
    return render(request, 'welcome.html')

def parent_inquiry(request):
    error_message = None
    if request.method == 'POST':
        parent_phone = request.POST.get('parent_phone', '').strip()
        if not parent_phone:
            error_message = "يرجى إدخال رقم الجوال"
        else:
            students = Student.objects.filter(parent_phone=parent_phone).select_related('teacher')

            for student in students:
                attendances = Attendance.objects.filter(student=student).order_by('-date')
                student.present_count = attendances.filter(status='حاضر').count()
                student.absent_count = attendances.filter(status='غائب').count()
                student.excused_count = attendances.filter(status='مستأذن').count()
                student.late_count = attendances.filter(status='متأخر').count()
                student.recent_attendance = attendances[:10]

                teacher_phone = None
                if student.teacher and hasattr(student.teacher, 'teacher_profile'):
                    teacher_phone = student.teacher.teacher_profile.phone
                student.teacher_phone = teacher_phone

            return render(
                request,
                'parent_inquiry_results.html',
                {
                    'students': students,
                    'parent_phone': parent_phone,
                }
            )

    return render(request, 'parent_inquiry.html', {'error_message': error_message})

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
        late = attendances.filter(status='متأخر').count()
        
        # عدد الأيام غير الحاضر (غياب + استئذان + تأخير)
        non_present_count = absent + excused + late
        
        # جميع الحضور مع الحالة
        all_attendance = list(attendances.values('date', 'status').order_by('-date'))
        
        attendance_stats[student.id] = {
            'student': student,
            'total_days': total_days,
            'present': present,
            'absent': absent,
            'excused': excused,
            'late': late,
            'non_present_count': non_present_count,
            'all_attendance': all_attendance
        }
    
    context = {
        'total_students': total_students,
        'attendance_stats': attendance_stats,
    }
    
    return render(request, 'teacher_dashboard.html', context)

@login_required
def update_attendance(request):
    """تحديث حالة الحضور من لوحة تحكم المعلم"""
    if request.method == 'POST':
        from datetime import datetime
        
        # جلب جميع البيانات المرسلة
        for key, value in request.POST.items():
            if key.startswith('status_'):
                # استخراج التاريخ والـ student_id
                # الصيغة: status_YYYY-MM-DD_student_id
                try:
                    # إزالة البادئة 'status_'
                    rest = key.replace('status_', '')
                    # فصل بآخر underscore لأن التاريخ قد يحتوي على شرطات
                    last_underscore = rest.rfind('_')
                    date_str = rest[:last_underscore]
                    student_id = rest[last_underscore+1:]
                    
                    attendance_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                    student = Student.objects.get(id=student_id, teacher=request.user)
                    
                    # تحديث حالة الحضور
                    attendance = Attendance.objects.filter(
                        student=student,
                        date=attendance_date
                    ).first()
                    
                    if attendance:
                        attendance.status = value
                        attendance.save()
                except (Student.DoesNotExist, ValueError):
                    pass
    
    return redirect('teacher_dashboard')

@login_required
def nominate_for_exam(request):
    """صفحة ترشيح الطلاب للاختبار الداخلي"""
    # جلب طلاب المعلم
    students = Student.objects.filter(teacher=request.user, status='منتظم')

    existing_nominations = ExamNomination.objects.filter(teacher=request.user)
    nomination_map = {item.student_id: item.id for item in existing_nominations}
    
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
        return redirect('teacher_nominations')
    
    return render(request, 'nominate_exam.html', {
        'students': students,
        'nomination_map': nomination_map,
    })


@login_required
def delete_nomination(request, nomination_id):
    """حذف ترشيح طالب من الاختبار"""
    nomination = get_object_or_404(ExamNomination, id=nomination_id, teacher=request.user)
    if request.method == 'POST':
        nomination.delete()
    next_url = request.POST.get('next') or 'teacher_nominations'
    return redirect(next_url)


@login_required
def delete_pending_student(request, student_id):
    """حذف طالب من قائمة المنتظرين"""
    if not is_stage_supervisor(request.user):
        return redirect('home')

    student = get_object_or_404(Student, id=student_id, status='منتظر')

    if not request.user.is_superuser and hasattr(request.user, 'stage_supervisor'):
        supervisor = request.user.stage_supervisor
        if student.educational_stage != supervisor.stage:
            return redirect('pending_students')

    if request.method == 'POST':
        student.delete()
    return redirect('pending_students')


@login_required
def teacher_nominations(request):
    """عرض الطلاب المرشحين من قبل المعلم"""
    nominations = ExamNomination.objects.filter(teacher=request.user).order_by('-id')

    nominations_with_next = []
    for nomination in nominations:
        nominations_with_next.append({
            'nomination': nomination,
            'next_part': nomination.get_next_part()
        })

    return render(request, 'teacher_nominations.html', {'nominations': nominations_with_next})

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
def preparer_take_attendance(request):
    """تحضير المعلمين - للمحضّر فقط"""
    if not user_has_role(request.user, 'preparer') and not request.user.is_superuser:
        return redirect('home')

    teachers = User.objects.filter(student__isnull=False).distinct().order_by('username')

    today = timezone.now().date()
    selected_date_str = request.POST.get('attendance_date') or request.GET.get('date') or str(today)
    try:
        selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
    except ValueError:
        selected_date = today

    weekday_map = {
        6: 'الأحد',
        0: 'الاثنين',
        1: 'الثلاثاء',
        2: 'الأربعاء',
        3: 'الخميس',
    }
    current_weekday = weekday_map.get(selected_date.weekday(), 'الأحد')
    current_week = AcademicCalendar.get_week_from_date(selected_date)

    success = False
    if request.method == 'POST':
        posted_date_str = request.POST.get('attendance_date', str(selected_date))
        try:
            posted_date = datetime.strptime(posted_date_str, "%Y-%m-%d").date()
        except ValueError:
            posted_date = selected_date

        selected_weekday = weekday_map.get(posted_date.weekday(), 'الأحد')
        selected_week = AcademicCalendar.get_week_from_date(posted_date)

        for teacher in teachers:
            status = request.POST.get(f'status_{teacher.id}')
            if status:
                TeacherAttendance.objects.update_or_create(
                    teacher=teacher,
                    date=posted_date,
                    defaults={
                        'status': status,
                        'weekday': selected_weekday,
                        'week_number': selected_week
                    }
                )

        success = True
        selected_date = posted_date
        current_weekday = selected_weekday
        current_week = selected_week

    existing_attendance = TeacherAttendance.objects.filter(teacher__in=teachers, date=selected_date)
    attendance_map = {item.teacher_id: item.status for item in existing_attendance}

    teachers_with_status = []
    for teacher in teachers:
        status = attendance_map.get(teacher.id, 'حاضر')
        display_name = teacher.get_full_name() or teacher.username
        teachers_with_status.append({
            'teacher': teacher,
            'display_name': display_name,
            'status': status,
        })

    context = {
        'teachers_with_status': teachers_with_status,
        'current_weekday': current_weekday,
        'current_week': current_week,
        'selected_date': selected_date,
        'today': today,
        'success': success,
    }

    return render(request, 'preparer_take_attendance.html', context)


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
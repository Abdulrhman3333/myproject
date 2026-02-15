import os
import django
import random
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth.models import User
from quran_center.models import (
    Student, Attendance, TeacherAttendance, ExamNomination, 
    AcademicCalendar, TeacherProfile
)

def generate_test_attendance_data():
    """Generate test attendance data for students"""
    students = Student.objects.all()[:20]  # Use first 20 students
    teachers = User.objects.filter(teacher_profile__isnull=False)[:5]
    
    # Get dates from the last 8 weeks
    today = datetime.now().date()
    start_date = today - timedelta(days=56)  # 8 weeks back
    
    weekdays = ['الأحد', 'الاثنين', 'الثلاثاء', 'الأربعاء', 'الخميس']
    statuses = ['حاضر', 'غائب', 'مستأذن', 'متأخر']
    
    attendance_count = 0
    
    for student in students:
        # Create attendance records for each student
        current_date = start_date
        while current_date <= today:
            # Only add attendance for weekdays (assuming Monday-Friday schedule)
            if current_date.weekday() < 5:
                weekday_name = weekdays[current_date.weekday()]
                
                # Check if record exists
                if not Attendance.objects.filter(student=student, date=current_date).exists():
                    # 80% chance of presence, 15% absence, 5% excuse
                    rand = random.random()
                    if rand < 0.80:
                        status = 'حاضر'
                    elif rand < 0.95:
                        status = 'غائب'
                    else:
                        status = 'مستأذن'
                    
                    week_number = 1 + (current_date - start_date).days // 7
                    
                    Attendance.objects.create(
                        student=student,
                        date=current_date,
                        weekday=weekday_name,
                        week_number=min(week_number, 19),
                        status=status
                    )
                    attendance_count += 1
            
            current_date += timedelta(days=1)
    
    print(f"✓ Created {attendance_count} student attendance records")
    return attendance_count


def generate_test_teacher_attendance_data():
    """Generate test attendance data for teachers"""
    teachers = User.objects.filter(teacher_profile__isnull=False)[:5]
    
    if not teachers:
        print("⚠ No teachers found. Create teachers first.")
        return 0
    
    today = datetime.now().date()
    start_date = today - timedelta(days=56)  # 8 weeks back
    
    weekdays = ['الأحد', 'الاثنين', 'الثلاثاء', 'الأربعاء', 'الخميس']
    statuses = ['حاضر', 'غائب', 'مستأذن', 'متأخر']
    
    attendance_count = 0
    
    for teacher in teachers:
        current_date = start_date
        while current_date <= today:
            if current_date.weekday() < 5:
                weekday_name = weekdays[current_date.weekday()]
                
                if not TeacherAttendance.objects.filter(teacher=teacher, date=current_date).exists():
                    rand = random.random()
                    if rand < 0.85:
                        status = 'حاضر'
                    elif rand < 0.97:
                        status = 'غائب'
                    else:
                        status = 'مستأذن'
                    
                    week_number = 1 + (current_date - start_date).days // 7
                    
                    TeacherAttendance.objects.create(
                        teacher=teacher,
                        date=current_date,
                        weekday=weekday_name,
                        week_number=min(week_number, 19),
                        status=status
                    )
                    attendance_count += 1
            
            current_date += timedelta(days=1)
    
    print(f"✓ Created {attendance_count} teacher attendance records")
    return attendance_count


def generate_test_exam_data():
    """Generate test exam nomination data"""
    students = Student.objects.all()[:15]
    teachers = User.objects.filter(teacher_profile__isnull=False)
    
    if not teachers:
        print("⚠ No teachers found. Create teachers first.")
        return 0
    
    part_choices = ['1', '2', '3', '5', '8', '10', '13', '15', '20', '25']
    exam_count = 0
    
    for student in students:
        # Skip if student doesn't have grade set
        if not student.grade:
            continue
        
        # Create 1-3 exam nominations per student
        for _ in range(random.randint(1, 3)):
            teacher = random.choice(teachers)
            last_tested = random.choice(part_choices)
            
            # Generate random grades
            teacher_grade = round(random.uniform(50, 100), 2)
            internal_grade = round(random.uniform(40, 98), 2)
            association_grade = round(random.uniform(40, 100), 2) if random.random() > 0.6 else None
            
            try:
                exam = ExamNomination.objects.create(
                    student=student,
                    teacher=teacher,
                    last_tested_part=last_tested,
                    teacher_grade=teacher_grade,
                    internal_grade=internal_grade,
                    association_grade=association_grade,
                    internal_passed=internal_grade >= 60,
                    association_tested=association_grade is not None
                )
                exam_count += 1
            except Exception as e:
                print(f"Error creating exam for {student.full_name}: {e}")
    
    print(f"✓ Created {exam_count} exam nomination records")
    return exam_count


def generate_teacher_profiles():
    """Ensure all teachers have profiles with phone numbers"""
    teachers = User.objects.filter(groups__name='معلم')
    
    if not teachers:
        teachers = User.objects.filter(username__startswith='teacher')
    
    if not teachers:
        print("⚠ No teachers found to assign profiles.")
        return 0
    
    created_count = 0
    for teacher in teachers:
        if not hasattr(teacher, 'teacher_profile'):
            # Generate random phone number in 05 format
            phone = f"05{random.randint(10000000, 99999999)}"
            TeacherProfile.objects.create(user=teacher, phone=phone)
            created_count += 1
    
    print(f"✓ Created/verified {created_count} teacher profiles")
    return created_count


def main():
    print("\n" + "="*60)
    print("Populating Database with Test Data")
    print("="*60 + "\n")
    
    # Check if we have students
    student_count = Student.objects.count()
    if student_count == 0:
        print("❌ No students found in database!")
        print("Please import students first using the import script.")
        return
    
    print(f"Found {student_count} students in database\n")
    
    # Generate teacher profiles
    generate_teacher_profiles()
    
    # Generate attendance data
    generate_test_attendance_data()
    generate_test_teacher_attendance_data()
    
    # Generate exam data
    generate_test_exam_data()
    
    print("\n" + "="*60)
    print("✓ Test data population completed successfully!")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()

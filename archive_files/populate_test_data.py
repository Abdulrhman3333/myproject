"""
Script to populate the database with test data for the Quran Center application
Run with: python manage.py shell < populate_test_data.py
Or: python populate_test_data.py
"""

import os
import django
import sys
from datetime import date

# Fix Windows console encoding for Arabic text
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth.models import User
from quran_center.models import Student, Attendance
from django.utils import timezone

# Create teachers (users)
print("Creating test teachers...")

# Create a teacher user if not exists
teacher1, created = User.objects.get_or_create(
    username='معلم_احمد',
    defaults={
        'first_name': 'أحمد',
        'last_name': 'العثمان',
        'email': 'ahmed@example.com'
    }
)
if created:
    teacher1.set_password('teacher123')
    teacher1.save()
    print(f"✓ Created teacher: {teacher1.username}")
else:
    print(f"✓ Teacher already exists: {teacher1.username}")

teacher2, created = User.objects.get_or_create(
    username='معلم_محمد',
    defaults={
        'first_name': 'محمد',
        'last_name': 'القحطاني',
        'email': 'mohammed@example.com'
    }
)
if created:
    teacher2.set_password('teacher123')
    teacher2.save()
    print(f"✓ Created teacher: {teacher2.username}")
else:
    print(f"✓ Teacher already exists: {teacher2.username}")

# Create test students
print("\nCreating test students...")

students_data = [
    {
        'full_name': 'عبدالله محمد الغامدي',
        'student_phone': '0501234567',
        'parent_phone': '0551234567',
        'identity_number': '1234567890',
        'parent_identity': '1987654321',
        'grade': '5_pri',
        'birth_date': date(2014, 3, 15),
        'last_tested_part': '1',
        'previous_center': 'مسجد النور',
        'neighborhood': 'حي النهضة',
        'teacher': teacher1,
        'status': 'منتظم'
    },
    {
        'full_name': 'خالد سعد الشهري',
        'student_phone': '0502345678',
        'parent_phone': '0552345678',
        'identity_number': '1234567891',
        'parent_identity': '1987654322',
        'grade': '3_med',
        'birth_date': date(2011, 7, 20),
        'last_tested_part': '3',
        'previous_center': '',
        'neighborhood': 'حي السلام',
        'teacher': teacher1,
        'status': 'منتظم'
    },
    {
        'full_name': 'فيصل أحمد الزهراني',
        'student_phone': '0503456789',
        'parent_phone': '0553456789',
        'identity_number': '1234567892',
        'parent_identity': '1987654323',
        'grade': '2_sec',
        'birth_date': date(2008, 11, 10),
        'last_tested_part': '5',
        'previous_center': 'مسجد الهدى',
        'neighborhood': 'حي الروضة',
        'teacher': teacher2,
        'status': 'منتظم'
    },
    {
        'full_name': 'عمر ناصر العنزي',
        'student_phone': '',
        'parent_phone': '0554567890',
        'identity_number': '1234567893',
        'parent_identity': '1987654324',
        'grade': '1_pri',
        'birth_date': date(2018, 5, 25),
        'last_tested_part': '0',
        'previous_center': '',
        'neighborhood': 'حي الملك فهد',
        'teacher': teacher2,
        'status': 'منتظم'
    },
    {
        'full_name': 'سلطان عبدالرحمن الدوسري',
        'student_phone': '0505678901',
        'parent_phone': '0555678901',
        'identity_number': '1234567894',
        'parent_identity': '1987654325',
        'grade': '4_pri',
        'birth_date': date(2015, 9, 8),
        'last_tested_part': '2',
        'previous_center': '',
        'neighborhood': 'حي العزيزية',
        'teacher': teacher1,
        'status': 'منتظر'
    },
    {
        'full_name': 'ياسر فهد المطيري',
        'student_phone': '0506789012',
        'parent_phone': '0556789012',
        'identity_number': '1234567895',
        'parent_identity': '1987654326',
        'grade': '1_med',
        'birth_date': date(2012, 12, 3),
        'last_tested_part': '8',
        'previous_center': 'مركز المدينة',
        'neighborhood': 'حي الفيصلية',
        'teacher': None,
        'status': 'منتظر'
    },
    {
        'full_name': 'راشد عبدالعزيز الحربي',
        'student_phone': '0507890123',
        'parent_phone': '0557890123',
        'identity_number': '2234567890',
        'parent_identity': '2987654321',
        'grade': '3_sec',
        'birth_date': date(2007, 2, 14),
        'last_tested_part': '13',
        'previous_center': '',
        'neighborhood': 'حي النزهة',
        'teacher': teacher2,
        'status': 'منتظم'
    },
    {
        'full_name': 'طلال حمد السليمان',
        'student_phone': '',
        'parent_phone': '0558901234',
        'identity_number': '2234567891',
        'parent_identity': '2987654322',
        'grade': '2_pri',
        'birth_date': date(2017, 6, 18),
        'last_tested_part': '0',
        'previous_center': '',
        'neighborhood': 'حي الخالدية',
        'teacher': teacher1,
        'status': 'منتظر'
    }
]

created_students = []
for student_data in students_data:
    try:
        student, created = Student.objects.get_or_create(
            identity_number=student_data['identity_number'],
            defaults=student_data
        )
        if created:
            created_students.append(student)
            print(f"✓ Created student: {student.full_name} - {student.get_grade_display()} - {student.status}")
        else:
            print(f"✓ Student already exists: {student.full_name}")
    except Exception as e:
        print(f"✗ Error creating student {student_data['full_name']}: {e}")

# Create attendance records for some students
print("\nCreating attendance records...")

today = timezone.now().date()
attendance_data = [
    {'student_index': 0, 'status': 'حاضر'},
    {'student_index': 1, 'status': 'حاضر'},
    {'student_index': 2, 'status': 'غائب'},
    {'student_index': 3, 'status': 'حاضر'},
    {'student_index': 6, 'status': 'مستأذن'},
]

for att_data in attendance_data:
    if att_data['student_index'] < len(created_students):
        student = created_students[att_data['student_index']]
        attendance, created = Attendance.objects.get_or_create(
            student=student,
            date=today,
            defaults={'status': att_data['status']}
        )
        if created:
            print(f"✓ Created attendance: {student.full_name} - {att_data['status']}")
        else:
            print(f"✓ Attendance already exists: {student.full_name}")

print("\n" + "="*50)
print("Test data population completed!")
print("="*50)
print("\nSummary:")
print(f"Total students in database: {Student.objects.count()}")
print(f"Students waiting (منتظر): {Student.objects.filter(status='منتظر').count()}")
print(f"Active students (منتظم): {Student.objects.filter(status='منتظم').count()}")
print(f"Attendance records: {Attendance.objects.count()}")
print("\nTeacher accounts:")
print(f"  - Username: معلم_احمد, Password: teacher123")
print(f"  - Username: معلم_محمد, Password: teacher123")
print("\nYou can now run: python manage.py runserver")

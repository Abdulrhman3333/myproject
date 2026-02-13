"""
سكريبت لإضافة التقويم الدراسي (19 أسبوع من 18 يناير إلى 4 يوليو 2026)
Run with: python setup_calendar.py
"""

import os
import sys
import django
from datetime import date, timedelta

# Fix Windows console encoding for Arabic text
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from quran_center.models import AcademicCalendar, StageSupervisor

print("إنشاء التقويم الدراسي...")
print("="*60)

# البداية: الأحد 18 يناير 2026
start_date = date(2026, 1, 18)

# التحقق من وجود البيانات
if AcademicCalendar.objects.exists():
    print("! التقويم الدراسي موجود مسبقاً")
else:
    # إنشاء 19 أسبوع
    for week in range(1, 20):
        week_start = start_date + timedelta(weeks=week-1)
        # كل أسبوع من الأحد إلى الخميس (5 أيام)
        week_end = week_start + timedelta(days=4)
        
        calendar_week, created = AcademicCalendar.objects.get_or_create(
            week_number=week,
            defaults={
                'start_date': week_start,
                'end_date': week_end
            }
        )
        
        if created:
            print(f"✓ الأسبوع {week}: من {week_start} إلى {week_end}")
        else:
            print(f"✓ الأسبوع {week} موجود مسبقاً")

print("\n" + "="*60)
print("تحديث المشرفين بالمراحل...")
print("="*60)

# تحديث المشرفين الحاليين
supervisors = StageSupervisor.objects.all()
if supervisors.exists():
    # تعيين مرحلة افتراضية للمشرفين الموجودين
    for idx, supervisor in enumerate(supervisors):
        stages = ['مبكرة', 'عليا', 'متوسط', 'ثانوي', 'جامعي']
        if not supervisor.stage:
            supervisor.stage = stages[idx % len(stages)]
            supervisor.save()
            print(f"✓ تم تعيين {supervisor.user.username} كمشرف مرحلة {supervisor.stage}")
        else:
            print(f"✓ {supervisor.user.username} - مشرف مرحلة {supervisor.stage}")
else:
    print("! لا يوجد مشرفين حالياً. استخدم add_supervisors.py لإضافة مشرفين.")

print("\n" + "="*60)
print("تم الإعداد بنجاح!")
print("="*60)
print(f"\nعدد الأسابيع الدراسية: {AcademicCalendar.objects.count()}")
print(f"عدد المشرفين: {StageSupervisor.objects.count()}")
print("\nيمكنك الآن تشغيل السيرفر: python manage.py runserver")

"""
Script to add stage supervisors and update test data
Run with: python add_supervisors.py
"""

import os
import django
import sys

# Fix Windows console encoding for Arabic text
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth.models import User
from quran_center.models import StageSupervisor, Student

print("Creating stage supervisors...")

# Create a stage supervisor from existing teacher
try:
    # Make معلم_احمد a stage supervisor (can be teacher and supervisor)
    teacher1 = User.objects.get(username='معلم_احمد')
    supervisor1, created = StageSupervisor.objects.get_or_create(
        user=teacher1,
        defaults={
            'can_approve_students': True,
            'can_assign_teachers': True
        }
    )
    if created:
        print(f"✓ Created stage supervisor: {teacher1.username}")
    else:
        print(f"✓ Stage supervisor already exists: {teacher1.username}")
except User.DoesNotExist:
    print("✗ User معلم_احمد not found. Please run populate_test_data.py first.")

# Create another dedicated stage supervisor
supervisor_user, created = User.objects.get_or_create(
    username='مشرف_خالد',
    defaults={
        'first_name': 'خالد',
        'last_name': 'المحمدي',
        'email': 'supervisor@example.com',
        'is_staff': True
    }
)
if created:
    supervisor_user.set_password('supervisor123')
    supervisor_user.save()
    print(f"✓ Created supervisor user: {supervisor_user.username}")
else:
    print(f"✓ Supervisor user already exists: {supervisor_user.username}")

supervisor2, created = StageSupervisor.objects.get_or_create(
    user=supervisor_user,
    defaults={
        'can_approve_students': True,
        'can_assign_teachers': True
    }
)
if created:
    print(f"✓ Created stage supervisor record: {supervisor_user.username}")
else:
    print(f"✓ Stage supervisor record already exists: {supervisor_user.username}")

print("\n" + "="*60)
print("Stage Supervisors Setup Completed!")
print("="*60)
print("\nStage Supervisor Accounts:")
print("1. Username: معلم_احمد, Password: teacher123")
print("   (This teacher is now also a stage supervisor)")
print("2. Username: مشرف_خالد, Password: supervisor123")
print("   (Dedicated stage supervisor)")
print("\nStage supervisors can:")
print("  - Accept pending students")
print("  - Assign teachers to students")
print("  - Also work as teachers if they have students assigned")
print("\nYou can now login and test the new permissions!")

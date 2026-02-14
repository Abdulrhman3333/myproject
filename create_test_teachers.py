import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth.models import User
from quran_center.models import TeacherProfile

def create_test_teachers():
    """Create test teacher accounts if they don't exist"""
    
    teacher_data = [
        {'username': 'المعلم1', 'first_name': 'أحمد', 'last_name': 'محمود'},
        {'username': 'المعلم2', 'first_name': 'محمد', 'last_name': 'علي'},
        {'username': 'المعلم3', 'first_name': 'فاطمة', 'last_name': 'حسن'},
        {'username': 'المعلم4', 'first_name': 'سارة', 'last_name': 'عبدالله'},
        {'username': 'المعلم5', 'first_name': 'علي', 'last_name': 'خالد'},
        {'username': 'المعلم6', 'first_name': 'نور', 'last_name': 'محمد'},
        {'username': 'المعلم7', 'first_name': 'ليلى', 'last_name': 'أحمد'},
        {'username': 'المعلم8', 'first_name': 'عمر', 'last_name': 'سالم'},
    ]
    
    created_count = 0
    for data in teacher_data:
        user, created = User.objects.get_or_create(
            username=data['username'],
            defaults={
                'first_name': data['first_name'],
                'last_name': data['last_name'],
                'email': f"{data['username']}@tahfeed.local",
                'is_staff': False,
                'is_active': True,
            }
        )
        
        if created:
            user.set_password('password123')
            user.save()
            print(f"✓ Created teacher: {data['username']}")
        
        # Create or update teacher profile
        profile, profile_created = TeacherProfile.objects.get_or_create(
            user=user,
            defaults={'phone': f"05{random.randint(10000000, 99999999)}"}
        )
        
        if profile_created:
            print(f"  └─ Created profile with phone: {profile.phone}")
        
        if created:
            created_count += 1
    
    return created_count


def main():
    print("\n" + "="*60)
    print("Creating Test Teachers")
    print("="*60 + "\n")
    
    created = create_test_teachers()
    
    total_teachers = User.objects.filter(teacher_profile__isnull=False).count()
    print(f"\n✓ Total teachers with profiles: {total_teachers}")
    print(f"✓ Newly created: {created}")
    print("\n" + "="*60)


if __name__ == '__main__':
    main()

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from quran_center.models import Student, TeacherProfile

def normalize_phone(phone_number):
    """
    Normalize phone numbers to 05 format.
    Converts +966, 966, or 5 to 05
    """
    if not phone_number:
        return phone_number
    
    # Remove spaces and common separators
    phone = str(phone_number).strip().replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
    
    # If starts with +966, replace with 05
    if phone.startswith('+966'):
        return '0' + phone[3:]  # +966XXXXXXX -> 0XXXXXXX (removes the +966 and adds 0)
    
    # If starts with 966, replace with 05
    if phone.startswith('966'):
        return '0' + phone[2:]  # 966XXXXXXX -> 0XXXXXXX
    
    # If starts with 5, prepend 0
    if phone.startswith('5') and len(phone) >= 9:
        return '0' + phone  # 5XXXXXXX -> 05XXXXXXX
    
    # If already in 05 format, return as is
    if phone.startswith('05'):
        return phone
    
    # Return unchanged if doesn't match patterns
    return phone_number


def normalize_students():
    """Normalize Student phone numbers"""
    students = Student.objects.all()
    updated_count = 0
    
    for student in students:
        changes = False
        
        if student.student_phone:
            normalized = normalize_phone(student.student_phone)
            if normalized != student.student_phone:
                print(f"Student {student.full_name}: student_phone '{student.student_phone}' -> '{normalized}'")
                student.student_phone = normalized
                changes = True
        
        if student.parent_phone:
            normalized = normalize_phone(student.parent_phone)
            if normalized != student.parent_phone:
                print(f"Student {student.full_name}: parent_phone '{student.parent_phone}' -> '{normalized}'")
                student.parent_phone = normalized
                changes = True
        
        if changes:
            student.save()
            updated_count += 1
    
    return updated_count


def normalize_teachers():
    """Normalize TeacherProfile phone numbers"""
    profiles = TeacherProfile.objects.all()
    updated_count = 0
    
    for profile in profiles:
        if profile.phone:
            normalized = normalize_phone(profile.phone)
            if normalized != profile.phone:
                print(f"Teacher {profile.user.username}: phone '{profile.phone}' -> '{normalized}'")
                profile.phone = normalized
                profile.save()
                updated_count += 1
    
    return updated_count


if __name__ == '__main__':
    print("=" * 60)
    print("Normalizing Phone Numbers to 05 Format")
    print("=" * 60)
    
    print("\nNormalizing Student phone numbers...")
    student_count = normalize_students()
    print(f"Updated {student_count} students")
    
    print("\nNormalizing Teacher phone numbers...")
    teacher_count = normalize_teachers()
    print(f"Updated {teacher_count} teachers")
    
    print("\n" + "=" * 60)
    print(f"Total records updated: {student_count + teacher_count}")
    print("=" * 60)

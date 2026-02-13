from django.contrib import admin
from .models import Student, Attendance

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    # الأعمدة التي تظهر في الجدول للمدير
    list_display = ('full_name', 'grade', 'educational_stage', 'status', 'teacher')
    
    # فلاتر جانبية للبحث السريع
    list_filter = ('status', 'educational_stage', 'teacher', 'grade')
    
    # إمكانية البحث بالاسم أو الهوية
    search_fields = ('full_name', 'identity_number')
    
    # إمكانية تعديل الحالة أو المعلم مباشرة من الجدول
    list_editable = ('status', 'teacher')

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'status')
    list_filter = ('date', 'status')
    search_fields = ('student__full_name',)
    date_hierarchy = 'date'


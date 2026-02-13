from django import forms
from .models import Student, LAST_TESTED_PART_CHOICES

class StudentRegistrationForm(forms.ModelForm):
    # تعريف خيارات آخر جزء تم اختباره
    last_tested_part = forms.ChoiceField(
        choices=LAST_TESTED_PART_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='آخر جزء تم اختباره'
    )
    
    class Meta:
        model = Student
        # نختار الحقول التي يدخلها الطالب فقط (الحالة والمرحلة تُحسب تلقائياً)
        fields = [
            'full_name', 'student_phone', 'parent_phone', 'identity_number', 
            'parent_identity', 'grade', 'birth_date', 'last_tested_part', 
            'previous_center', 'neighborhood'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'student_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'parent_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'identity_number': forms.TextInput(attrs={'class': 'form-control'}),
            'parent_identity': forms.TextInput(attrs={'class': 'form-control'}),
            'grade': forms.Select(attrs={'class': 'form-select'}),
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'previous_center': forms.TextInput(attrs={'class': 'form-control'}),
            'neighborhood': forms.TextInput(attrs={'class': 'form-control'}),
        }

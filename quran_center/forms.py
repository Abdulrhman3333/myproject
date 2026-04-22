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
            'grade', 'last_tested_part', 
            'previous_center', 'neighborhood'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'student_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'parent_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'identity_number': forms.TextInput(attrs={'class': 'form-control'}),
            'grade': forms.Select(attrs={'class': 'form-select'}),
            'previous_center': forms.TextInput(attrs={'class': 'form-control'}),
            'neighborhood': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # اجعل كل الحقول المعروضة مطلوبة في نموذج التسجيل
        for field_name, field in self.fields.items():
            field.required = True
            field.widget.attrs['required'] = 'required'

        # تقييد الحقول الرقمية لتكون 10 أرقام بالواجهة
        for numeric_field in ['identity_number', 'student_phone', 'parent_phone']:
            self.fields[numeric_field].widget.attrs.update({
                'pattern': r'\d{10}',
                'maxlength': '10',
                'minlength': '10',
                'inputmode': 'numeric',
            })

    def _clean_ten_digits(self, field_name, label):
        value = (self.cleaned_data.get(field_name) or '').strip()
        if not value.isdigit() or len(value) != 10:
            raise forms.ValidationError(f"{label} يجب أن يتكون من 10 أرقام.")
        return value

    def clean_identity_number(self):
        return self._clean_ten_digits('identity_number', 'رقم هوية الطالب')

    def clean_student_phone(self):
        return self._clean_ten_digits('student_phone', 'جوال الطالب')

    def clean_parent_phone(self):
        return self._clean_ten_digits('parent_phone', 'جوال ولي الأمر')


class StudentBulkUploadForm(forms.Form):
    excel_file = forms.FileField(
        label='ملف Excel',
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.xlsx'})
    )

    def clean_excel_file(self):
        excel_file = self.cleaned_data['excel_file']
        filename = excel_file.name.lower()

        if not filename.endswith('.xlsx'):
            raise forms.ValidationError('يرجى رفع ملف Excel بصيغة .xlsx')

        return excel_file

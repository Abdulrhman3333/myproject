from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

# تعريف قاعدة: يجب أن يكون الرقم 10 خانات ويبدأ بـ 1 أو 2
id_validator = RegexValidator(regex=r'^[12]\d{9}$', message="رقم الهوية غير صحيح")

class Student(models.Model):

    identity_number = models.CharField(
        max_length=10, 
        validators=[id_validator], 
        unique=True,
        verbose_name="رقم الهوية"
    )
    
    # خيارات الصف الدراسي
    GRADE_CHOICES = [
        ('1_pri', 'أولى ابتدائي'), ('2_pri', 'ثانية ابتدائي'), ('3_pri', 'ثالثة ابتدائي'),
        ('4_pri', 'رابعة ابتدائي'), ('5_pri', 'خامسة ابتدائي'), ('6_pri', 'سادسة ابتدائي'),
        ('1_med', 'أول متوسط'), ('2_med', 'ثاني متوسط'), ('3_med', 'ثالث متوسط'),
        ('1_sec', 'أول ثانوي'), ('2_sec', 'ثاني ثانوي'), ('3_sec', 'ثالث ثانوي'),
        ('uni', 'جامعي'),
    ]

    STATUS_CHOICES = [('منتظر', 'منتظر'), ('منتظم', 'منتظم')]

    # البيانات المطلوبة
    full_name = models.CharField(max_length=200, verbose_name="الاسم الثلاثي")
    student_phone = models.CharField(max_length=15, blank=True, null=True, verbose_name="جوال الطالب")
    parent_phone = models.CharField(max_length=15, verbose_name="جوال ولي الأمر")
    identity_number = models.CharField(max_length=10, unique=True, verbose_name="رقم الهوية")
    parent_identity = models.CharField(max_length=10, verbose_name="رقم هوية ولي الأمر")
    grade = models.CharField(max_length=20, choices=GRADE_CHOICES, verbose_name="الصف الدراسي")
    birth_date = models.DateField(verbose_name="تاريخ الميلاد")
    last_tested_part = models.CharField(max_length=50, verbose_name="آخر جزء تم اختباره")
    previous_center = models.CharField(max_length=100, blank=True, null=True, verbose_name="التحفيظ السابق")
    neighborhood = models.CharField(max_length=100, verbose_name="الحي")
    
    # حقول تلقائية
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="المعلم المسؤول")
    status = models.CharField(max_length=20, default='منتظر', choices=STATUS_CHOICES)
    educational_stage = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # أتمتة المرحلة الدراسية بناءً على الصف
        primary_early = ['1_pri', '2_pri', '3_pri']
        primary_late = ['4_pri', '5_pri', '6_pri']
        intermediate = ['1_med', '2_med', '3_med']
        secondary = ['1_sec', '2_sec', '3_sec']

        if self.grade in primary_early:
            self.educational_stage = "مبكرة"
        elif self.grade in primary_late:
            self.educational_stage = "عليا"
        elif self.grade in intermediate:
            self.educational_stage = "متوسط"
        elif self.grade in secondary:
            self.educational_stage = "ثانوي"
        else:
            self.educational_stage = "جامعي"
            
        super(Student, self).save(*args, **kwargs)

    def __str__(self):
        return self.full_name
    

class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=[
        ('حاضر', 'حاضر'),
        ('غائب', 'غائب'),
        ('مستأذن', 'مستأذن')
    ], default='حاضر')

    class Meta:
        unique_together = ('student', 'date') # لمنع التحضير مرتين لنفس الطالب في نفس اليوم
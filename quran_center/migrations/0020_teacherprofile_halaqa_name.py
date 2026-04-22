from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quran_center', '0019_alter_attendance_status_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='teacherprofile',
            name='halaqa_name',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='اسم الحلقة'),
        ),
    ]

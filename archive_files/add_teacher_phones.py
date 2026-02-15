"""
Script to update teacher phone numbers.
Run with: python add_teacher_phones.py
"""

import os
import sys

# Fix Windows console encoding for Arabic text
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

import django

django.setup()

from django.contrib.auth.models import User
from quran_center.models import TeacherProfile

TEACHER_PHONES = {
    "حسن امام": "0564982999",
    "باسم فتني": "0565152720",
    "محمد ابو بكر": "0563664808",
    "عبدالمجيب رجب": "0569421236",
    "عبدالرحمن بن محفوظ": "0545823188",
    "عمر باظراح": "0531010120",
    "علي عنتر": "0556052500",
    "بندر نصر": "0551022538",
    "عامر الحربي": "0538823430",
    "مجاهد باحمدين": "0541514312",
    "عبدالرحمن باغشير": "0538914185",
    "احمد نورولي": "0501517951",
    "اسامة حديدي": "0567835887",
    "عبدالله مهرات": "0501203935",
    "معاذ الاهدل": "0531254876",
    "عبدالله العمودي - العصر": "0556642003",
    "عبدالله حلبي": "0500492607",
    "محمد باعباد": "0507973125",
    "مؤيد نورولي": "0548088977",
    "حسان عنتر": "0563004867",
    "صفوان مهرات": "0559824393",
    "هشام حافظ": "0530218680",
    "محمد الحميري": "0594299800",
    "زكريا نورولي": "0554602825",
    "احمد الشيخي": "0564486758",
    "عبدالله العمودي - المغرب": "0556642003",
}

updated = 0
missing = []

for username, phone in TEACHER_PHONES.items():
    user = User.objects.filter(username=username).first()
    if not user:
        missing.append(username)
        continue

    profile, _created = TeacherProfile.objects.get_or_create(user=user)
    profile.phone = phone
    profile.save()
    updated += 1
    print(f"✓ Updated {username} -> {phone}")

print("\n" + "=" * 60)
print(f"Updated: {updated}")
if missing:
    print("Missing users (no update applied):")
    for name in missing:
        print(f"- {name}")
else:
    print("All users were updated successfully.")

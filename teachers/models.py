from django.db import models
from django.contrib.auth.models import User
from grades.models import Grade

# Create your models here.
GENDER_CHOICES=[
    ('M','男'),
    ('F','女')
]

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher')
    teacher_name = models.CharField(max_length=50, verbose_name='老师姓名')
    phone_number = models.CharField(max_length=11, unique=True, verbose_name='手机号')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name='性别')
    birthday = models.DateField(verbose_name='出生日期', help_text='格式例如：2020-05-01') 
    grade = models.OneToOneField(Grade, on_delete=models.DO_NOTHING, verbose_name='管理班级')

    def __str__(self)->str:
        return self.teacher_name
    
    class Meta:
        db_table="teacher"
        verbose_name_plural="老师信息"
        verbose_name="老师信息"
from django.db import models
#导入user管理员表 和此处得user关联起来
from django.contrib.auth.models import User
#导入班级表 
from grades.models import Grade

# Create your models here.
GENDER_CHOICES = [
    ('M', '男'),
    ('F', '女'),
]
class Student(models.Model):
    student_number = models.CharField(max_length=20, unique=True,verbose_name='学籍号')
    student_name = models.CharField(max_length=50, verbose_name='姓名')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name='性别')
    birthday = models.DateField(verbose_name='出生日期', help_text='格式例如：2020-05-01') 
    contact_number = models.CharField(max_length=20, verbose_name='联系方式')
    address = models.TextField(verbose_name='家庭住址')

    # user表一对一关联
    user = models.OneToOneField(User, on_delete=models.CASCADE) # 设置外键

    # 班级表一对多关联
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name='students', verbose_name='班级')
    
    def __str__(self):
        return self.student_name
    
    class Meta:
        db_table = "student"
        verbose_name_plural = "学生信息"
        verbose_name = "学生信息"
from django.db import models

from students.models import Grade

# Create your models here.
class Score(models.Model):
    title = models.CharField(max_length=20,help_text='title/考试名称',verbose_name='考试名称')
    student_number = models.CharField(max_length=20,verbose_name='学号')
    student_name = models.CharField(max_length=20,help_text='name/姓名',verbose_name='姓名')
    chinese_score = models.DecimalField(max_digits=5,decimal_places=2,help_text='score/语文分数',verbose_name='语文分数')
    math_score = models.DecimalField(max_digits=5,decimal_places=2,help_text='score/数学分数',verbose_name='数学分数')
    english_score = models.DecimalField(max_digits=5,decimal_places=2,help_text='score/英语分数',verbose_name='英语分数')
    # 班级表一对多关联
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name='score', verbose_name='班级')

    def __str__(self) -> str:
        return self.title

    class Meta:
        db_table = "score"
        verbose_name_plural = "成绩信息"
        verbose_name = "成绩信息"
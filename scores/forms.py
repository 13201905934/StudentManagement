from django import forms
from django.core.exceptions import ValidationError

from grades.models import Grade
from scores.models import Score
from students.models import Student



class ScoreForm(forms.ModelForm):
    class Meta:
        model=Score
        #展示字段
        fields=['title', 'student_name','student_number', 'grade','chinese_score', 'math_score', 'english_score']

        def __init__(self,*args,**kwargs):
            super.init__(*self,*args,**kwargs)
            self.fields['grade'].queryset=Grade.objects.all()
            self.fields['grade'].empty_lable='请选择班级'
    
    #学号校验
    def clean_student_number(self):
        student_number=self.cleaned_data['student_number']
        if len(student_number)!=8:
            raise ValidationError("学号必须8位长度")
        if not Student.objects.filter(student_number=student_number).exists():
            raise ValidationError("此学号不存在")
        return student_number
    
    #名字校验
    def clean_student_name(self):
        student_name = self.cleaned_data['student_name']
        if len(student_name) < 2 or len(student_name) > 50:
            raise ValidationError("名字长度在2-59之间")
        if not Student.objects.filter(student_name=student_name).exists():
            raise ValidationError("该学生姓名不存在")
        return student_name


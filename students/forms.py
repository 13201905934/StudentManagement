from django import forms
#导入日期
import datetime
from grades.models import Grade
from .models import Student
#验证错误异常
from django.core.exceptions import ValidationError

class StudentForm(forms.ModelForm):
    #根据grade_number对班级从小到大排序
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields.get('grade').queryset=Grade.objects.all().order_by('grade_number')
    #验证学生姓名
    def clean_student_name(self):
        #cleaned_data 获取表单提交所有数据
        student_name=self.cleaned_data.get('student_name')
        if len(student_name)<2 or len(student_name)>40:
            raise ValidationError('please input crroct name')
        #正常情况
        return student_name
    
    #验证学号
    def clean_student_number(self):
        student_number=self.cleaned_data.get('student_number')
        if len(student_number)!=8:
            raise ValidationError('学号长度应为8位')
        return student_number
        
    #验证生日
    def clean_birthday(self):
        birthday=self.cleaned_data.get('birthday')
        if not isinstance(birthday,datetime.date):
            raise ValidationError('生日格式错误，正确格式例如:1998-05-02')
        if birthday>datetime.date.today():
            raise ValidationError('生日应该在今天之前')
        return birthday

    #验证手机号
    def clean_contact_number(self):
        contact_number=self.cleaned_data.get('contact_number')
        if len(contact_number) != 11:
            raise ValidationError('the phone number should be 11')
        return contact_number

    class Meta:
        model=Student
        #展示字段
        fields = ['student_name', 'student_number', 'grade', 'gender', 'birthday', 'contact_number', 'address']

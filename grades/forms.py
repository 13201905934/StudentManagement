#从django中继承表单
from django import forms

from grades.models import Grade

#定义表单类 forms.ModelForm:表单用的字段都在model里 所以用这个
class GradeForm(forms.ModelForm):

    class Meta:
        model=Grade
        #展示字段
        fields=['grade_name','grade_number']

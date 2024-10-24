from django import forms
from django.core.exceptions import ValidationError


ROLE_CHOICES = [
    ('admin', '管理员'),
    ('teacher', '老师'),
    ('student', '学生'),
]


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入手机号或学号'}),
    )
    password = forms.CharField(
        max_length=50,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请输入密码'}),
    )
    role = forms.ChoiceField(label='角色', choices=ROLE_CHOICES)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if len(username) == 0:
            raise ValidationError('用户名长度不能为0。')
        return username

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) == 0:
            raise ValidationError('密码长度不能为0。')
        return password
    

    def clean_role(self):
        role = self.cleaned_data.get('role')
        if role not in ['admin','student', 'teacher']:
            raise ValidationError('请选择一个用户身份')
        return role
    


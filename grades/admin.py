from django.contrib import admin
from grades.models import Grade

# Register your models here.
#将班级注册到后台
admin.site.register(Grade)
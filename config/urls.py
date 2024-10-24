"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from accounts import views
from django.views.generic.base import RedirectView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/students/', permanent=False)),
    path('grades/',include('grades.urls')),
    #学生路由配置
    path('students/',include('students.urls')),
    #老师路由配置
    path('teachers/',include('teachers.urls')),
    #成绩路由管理
    path('scores/',include('scores.urls')),
    #登录界面路由管理
    path('login/',views.user_login,name='user_login'),
    #退出路由管理
    path('logout/',views.user_logout,name='user_logout'),
    #修改密码
    path('change_password/',views.change_password,name='change_password')
]

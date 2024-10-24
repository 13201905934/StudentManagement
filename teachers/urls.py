from django.contrib import admin
from django.urls import path
from .views import TeacherListView,TeacherCreateView,TeacherDeleteView,TeacherUpdateView

urlpatterns=[
    #查看学生列表
    path('',TeacherListView.as_view(),name='teacher_list'),
    #老师信息视图创建
    path('create/',TeacherCreateView.as_view(),name='teacher_create'),
    #老师信息删除
    path('<int:pk>/delete/',TeacherDeleteView.as_view(),name='teacher_delete'),
    #老师信息编辑
    path('<int:pk>/update/',TeacherUpdateView.as_view(),name='teacher_update'),
]
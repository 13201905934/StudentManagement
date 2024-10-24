from django.contrib import admin
from django.urls import path
from .views import (StudentListView,StudentCreateView,
                    StudentUpdateView,StudentDeleteView,
                    StudentBulkDeleteView,upload_student,
                    export_excel)

urlpatterns = [
    #查看学生列表
    path('',StudentListView.as_view(),name='student_list'),
    #学生信息创建视图
    path('create/',StudentCreateView.as_view(),name='student_create'),
    #学生编辑
    path('<int:pk>/update/',StudentUpdateView.as_view(),name='student_update'),
    #学生删除
    path('<int:pk>/delete/',StudentDeleteView.as_view(),name='student_delete'),
    #学生批量删除
    path('bulk_delete/',StudentBulkDeleteView.as_view(),name='student_bulk_delete'),
    #学生导入
    path('upload_student',upload_student,name='upload_student'),
    #学生信息导出
    path('export_excel',export_excel,name='export_excel')
    
]
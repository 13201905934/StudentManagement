from django.contrib import admin
from django.urls import path
from .views import GradeCreateView, GradeListView, GradeUpdateView,GradeDeleteView

urlpatterns = [
    #name=grades_list 在前台form表单提交时指定路径就是这个
    path('',GradeListView.as_view(),name='grades_list'),
    #创建班级路由
    path('create/',GradeCreateView.as_view(),name='grade_create'),
    #编辑班级路由
    path('<int:pk>/update/',GradeUpdateView.as_view(),name='grade_update'),
    #删除年级
    path('<int:pk>/delete/',GradeDeleteView.as_view(),name='grade_delete')
]
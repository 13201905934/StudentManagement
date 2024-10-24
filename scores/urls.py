from django.urls import path
from .views import (ScoreListView,ScoreCreateView,
                    ScoreUpdateView,ScoreDeleteView,
                    ScoreDetailView,ScoreBulkDeleteView,
                    upload_score,export_excel,
                    MyScoreListView)

urlpatterns=[
    #查看成绩列表
    path('',ScoreListView.as_view(),name='score_list'),
    #创建成绩信息
    path('create/',ScoreCreateView.as_view(),name='score_create'),
    #编辑学生信息
    path('<int:pk>/update/',ScoreUpdateView.as_view(),name='score_update'),
    #删除学生信息
    path('<int:pk>/delete/',ScoreDeleteView.as_view(),name='score_delete'),
    #学生成绩详情查看
    path('<int:pk>/detail/',ScoreDetailView.as_view(),name='score_detail'),
    #学生成绩批量删除
    path('bulk_delete/',ScoreBulkDeleteView.as_view(),name='score_bulk_delete'),
    #学生成绩导入
    path('upload_score',upload_score,name='upload_score'),
    #学生成绩导出
    path('export_excel',export_excel,name='export_excel'),
    #个人成绩查询
    path('my_score/',MyScoreListView.as_view(),name='my_scores')
]
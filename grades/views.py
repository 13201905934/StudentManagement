from django.shortcuts import render
#导入listview 创建视图 更新视图
from django.views.generic import ListView,CreateView,UpdateView,DeleteView
#导入模型
from .models import Grade
#导入Q函数用于查询
from django.db.models import Q
#导入表单
from .forms import GradeForm
#导入成功后跳转路径
from django.urls import reverse_lazy
from utils.permissions import RoleRequiredMixin

# Create your views here.
class GradeListView(RoleRequiredMixin,ListView):
    model=Grade
    template_name='grades/grades_list.html'
    #要展示字段
    fields=['grade_name','grade_number']
    #获取数据 'grades' 在前台遍历时就可以获取数据
    context_object_name='grades'
    #设置分页 =1则表示每页最多显示1条数据 会有个变量page_obj传到前台
    paginate_by=2
    #查看权限设置
    allowed_roles = ['admin']

    #重写查询方法
    def get_queryset(self):
        #使用搜索方法
        queryset=super().get_queryset()
        #获取搜索数据
        search=self.request.GET.get('search')
        if search:
            #根据班级名称、编号搜索
            queryset=queryset.filter(
                Q(grade_name__icontains=search)|
                Q(grade_number__icontains=search)
            )
        #满足条件则返回搜索结果
        return queryset
    
#新建班级
class GradeCreateView(RoleRequiredMixin,CreateView):
    model=Grade
    #指定模板
    template_name='grades/grades_form.html'
    #添加表单
    form_class=GradeForm
    #成功后跳转 ☞列表页面 
    success_url = reverse_lazy('grades_list')


#编辑班级
class GradeUpdateView(RoleRequiredMixin,UpdateView):
    model=Grade
    template_name='grades/grades_form.html'
    form_class=GradeForm
    success_url = reverse_lazy('grades_list')

#删除班级
class GradeDeleteView(RoleRequiredMixin,DeleteView):
    model=Grade
    template_name='grades/grade_delete_confirm.html'
    success_url=reverse_lazy('grades_list')
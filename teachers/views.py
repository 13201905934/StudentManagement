import json
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView,CreateView,DeleteView,UpdateView
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib.auth.hashers import make_password


from grades.models import Grade
from teachers.forms import TeacherForm
from teachers.models import Teacher

class BaseTeacherView():
    model=Teacher
    success_url = reverse_lazy('teacher_list')  # 创建成功后重定向的URL

# Create your views here.
class TeacherListView(ListView):
    #关联模型
    model=Teacher
    #前台页面路径
    template_name='teachers/teachers_list.html'
    #展示给前端的数据
    context_object_name='teachers'
    # 创建成功后重定向的URL
    success_url = reverse_lazy('teacher_list')
    #分页
    paginate_by=2

    def get_context_data(self):
        context=super().get_context_data()
        #获取所有班级并添加到上下文
        context['grades']=Grade.objects.all().order_by('grade_number')
        context['current_grade']=self.request.GET.get('grade','')
        return context
    
    #查询方法
    def get_queryset(self):
        queryset=super().get_queryset()
        # 获取搜索的内容
        keyword=self.request.GET.get('search')
        # 获取班级
        grade_id=self.request.GET.get('grade')
        if grade_id:
            queryset=queryset.filter(grade__pk=grade_id)
        if keyword:
            #根据姓名、电话搜索
            queryset=queryset.filter(
                Q(teacher_name__icontains=keyword)|
                Q(phone_number__icontains=keyword)
            )
        return queryset


#老师信息视图创建
class TeacherCreateView(CreateView):
    model=Teacher
    template_name='teachers/teacher_form.html'
    #定义表单
    form_class=TeacherForm

    def form_valid(self,form):
        #接受字段
        teacher_name=form.cleaned_data.get('teacher_name')
        phone_number=form.cleaned_data.get('phone_number')
        #写入到auth_user表
        username=teacher_name+'_'+phone_number
        #密码取后六位
        password=phone_number[-6:]
        #查看要写入的用户是否存在
        users=User.objects.filter(username=username)
        if users.exists():
            user=users.first()
        else:
            #创建auth_user表记录
            user=User.objects.create_user(username=username,password=password)
        #将新创建的用户关联到Student实例
        form.instance.user=user
        form.save()

        data={
            "status":"success",
            "messages":"successful"
            }
        # 返回json响应
        return HttpResponse(json.dumps(data),content_type='application/json;charset=utf-8')
    
    def form_invalid(self,form):
        errors=form.errors.as_json()
        return JsonResponse({
            "status":"error",
            "messagess":errors
        },status=400)

#学生删除
class TeacherDeleteView(BaseTeacherView,DeleteView):
    success_url=reverse_lazy('teacher_list')
    success_url = reverse_lazy('teacher_list')  # 创建成功后重定向的URL
    model=Teacher
    #删除
    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        if response.status_code == 302:
            return JsonResponse({'status': 'success', 'messages': '学生已删除'},status=200)
        else:
            return JsonResponse({'status': 'error', 'messages': '删除失败'}, status=400)

#老师编辑
class TeacherUpdateView(UpdateView):
    model=Teacher
    template_name='teachers/teacher_form.html'
    #定义表单
    form_class=TeacherForm

    def form_valid(self,form):
        #老师实例对象获取
        teacher=form.save(commit=False)
        #检查是否修改teacher_name phone_number changed_data：表中修改的数据会存在这里
        if 'teacher_name' or 'phone_number' in form.changed_data():
            teacher.user.username=form.cleaned_data.get('teacher_name')+'_'+form.cleaned_data.get('phone_number')
            #使用make_password对密码加密
            teacher.user.password=make_password(form.cleaned_data.get('phone_number')[-6:])
            #保存更改的用户模型
            teacher.user.save()
        #保存teacher模型
        teacher.save()
        #响应
        data={
            "status":"success",
            "messages":"successful"
            }
        #返回json响应
        return HttpResponse(json.dumps(data),content_type='application/json;charset=utf-8')
    #校验失败响应
    def form_invalid(self,form):
        errors=form.errors.as_json()
        return JsonResponse({
            "status":"error",
            "messages":errors
        },status=400)

    


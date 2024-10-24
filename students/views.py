import datetime
from pathlib import Path

import json
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.generic import ListView,CreateView,UpdateView,DeleteView
from django.contrib.auth.models import User
#对密码加密
from django.contrib.auth.hashers import make_password
#导入成功后跳转路径
from django.urls import reverse_lazy

from grades.models import Grade
from students.models import Student
#导入表单
from .forms import StudentForm

from django.db.models import Q
from utils.handle_excel import ReadExcel
import openpyxl
from io import BytesIO
#导入权限校验工具类
from utils.permissions import RoleRequiredMixin, role_required

# Create your views here.
class BaseStudentView(RoleRequiredMixin):
    #设置可访问权限列表
    allowed_roles = ['admin', 'teacher']

class StudentListView(BaseStudentView,ListView):
    #关联模型
    model=Student
    template_name='students/students_list.html'
    #展示给前端的数据
    context_object_name='students'
    #分页
    paginate_by=10

    def get_context_data(self):
        context = super().get_context_data()
        # 获取所有班级并添加到上下文
        context['grades'] = Grade.objects.all().order_by('grade_number')
        context['current_grade'] = self.request.GET.get('grade', '')
        return context

    #重写查询方法
    def get_queryset(self):
        queryset=super().get_queryset()
        #获取搜索的内容
        keyword=self.request.GET.get('search')
        #获取班级
        grade_id=self.request.GET.get('grade')
        if grade_id:
            queryset=queryset.filter(grade__pk=grade_id)
        if keyword:
            #根据姓名、学号搜索
            queryset=queryset.filter(
                Q(student_number__icontains=keyword)|
                Q(student_name__icontains=keyword)
            )
        #满足搜索则返回查询结果
        return queryset
    
        

class StudentCreateView(BaseStudentView,CreateView):
    model=Student
    template_name='students/student_form.html'
    #定义表单
    form_class=StudentForm

    def form_valid(self, form):
        #接受字段
        student_name=form.cleaned_data.get('student_name')
        student_number=form.cleaned_data.get('student_number')
        #写入到auth_user表
        username=student_name+'_'+student_number
        #密码取后六位
        password=student_number[-6:]
        #查看要写入的用户是否存在
        users=User.objects.filter(username=username)
        if users.exists():
            #表中存在则取第一个用户
            user=users.first()
        else:
            #创建auth_user表记录
            user=User.objects.create_user(username=username,password=password)
        #写入到student
        form.instance.user=user
        form.save()

        data={
            "status":"success",
            "messages":"successful"
            }
        # 返回json响应
        return HttpResponse(json.dumps(data),content_type='application/json;charset=utf-8')
    
    #forms中对手机号等等字段校验失败后执行该方法
    def form_invalid(self,form):
        errors=form.errors.as_json()
        return JsonResponse({
            "status":"error",
            "messages":errors
        },status=400)
    
class StudentUpdateView(BaseStudentView,UpdateView):
    model=Student
    template_name='students/student_form.html'
    #定义表单
    form_class=StudentForm

    def form_valid(self,form):
        #获取学生对象实例 commit=False 不提交
        student=form.save(commit=False)
        #检查是否修改 student_name student_number changed_data:表中修改的数据会存在这里
        if 'student_name' or 'student_number' in form.changed_data:
            student.user.username=form.cleaned_data.get('student_name')+'_'+form.cleaned_data.get('student_number')
            #make_password 对密码加密
            student.user.password=make_password(form.cleaned_data.get('student_number')[-6:])
            #保存更改的用户模型
            student.user.save()
        #保存student模型
        student.save()
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
            "messages":errors
        },status=400)

#学生删除
class StudentDeleteView(BaseStudentView,DeleteView):
    success_url=reverse_lazy('student_list')
    model=Student
    #删除
    def delete(self,request, *args, **kwargs):
        #获取当前对象
        self.object=self.get_object()
        try:
            #删除成功
            self.object.delete()
            return JsonResponse({
                "status":"success",
                "messages":"删除成功"
            },status=200)
        except Exception as e:
            return JsonResponse({
                "status":"error",
                "messages":"删除失败"+str(e)
            },status=500)

#学生批量删除
class StudentBulkDeleteView(BaseStudentView,DeleteView):
    success_url=reverse_lazy('student_list')
    model=Student

    def post(self,request, *args, **kwargs):
        #获取前台提交的要删除的学生列表
        selected_ids=request.POST.getlist('student_ids')
        #列表为空 则返回提示
        if not selected_ids:
            return JsonResponse({
                "status":"error",
                "messages":"请选择要删除的学生信息"
            },status=400)
        #获取所有id在selected_ids中的学生信息
        self.object_list=self.get_queryset().filter(id__in=selected_ids)

        try:
            #删除
            self.object_list.delete()
            return JsonResponse({
                "status":"success",
                "messages":"删除成功"
            },status=200)
        except Exception as e:
            return JsonResponse({
                "status":"error",
                "messages":"删除失败"+str(e)
            },status=500)

#学生信息导入
@role_required('admin','teacher')        
def upload_student(request):
    #上传学生信息excel文件
    if request.method=='POST':
        #获取文件
        file=request.FILES.get('excel_file')
        #判断文件是否上传
        if not file:
            return JsonResponse({
                'status':'error',
                'messages':'请上传excel文件'
            },status=200)
        #判断文件类型是否为excel suffix:获取后缀
        ext=Path(file.name).suffix
        if ext.lower() !='.xlsx':
            return JsonResponse({
                'status':'error',
                'messages':'文件类型错误，请上传.excel文件'
            },status=400)
        #openpyxl读取excel文件内容
        read_excel=ReadExcel(file)
        data=read_excel.get_data()
        if data[0] !=['班级','姓名','学号','性别','出生日期','联系电话','家庭住址']:
            return JsonResponse({
                'status':'error',
                'messages':'Excel中学生信息不是指定格式'
            })
        #将excel学生信息写入数据库
        for row in data[1:]:
            grade, student_name, student_number, gender, birthday, contact_number, address = row
            #检查班级是否存在
            grade=Grade.objects.filter(grade_name=grade).first()
            if not grade:
                return JsonResponse({
                    'status':'error',
                    'messages':f'{grade}不存在'
                },status=400)
            # 检测主要字段
            if not student_name:
                return JsonResponse({'status': 'error', 'messages': '学生姓名不能为空'}, status=400)
            if not student_number or len(student_number) != 8:
                return JsonResponse({'status': 'error', 'messages': '学籍号不能为空，并且长度应为8位'}, status=400)
            # 检查日期格式
            if not isinstance(birthday, datetime.datetime) :
                return JsonResponse({'status': 'error', 'messages': '出生日期格式错误'}, status=400)
            # 判断学生信息是否存在
            if Student.objects.filter(student_number=student_number).exists():
                return JsonResponse({'status': 'error', 'messages': f'学号{student_number}已经存在'}, status=400)

            #写入数据库
            try:
                #判断auth_user表中学生数据是否存在，不存在时则在auth_user中创建用户
                username=student_name+'_'+student_number
                users=User.objects.filter(username=username)
                if users.exists():
                    users=users.first()
                else:
                    password=student_number[-6:]
                    user=User.objects.create_user(username=username,password=password)
                #在student表创建记录：
                Student.objects.create(
                    student_name=student_name,
                    student_number=student_number,
                    grade=grade,
                    gender='M' if gender=='男' else 'F',
                    birthday=birthday,
                    contact_number = contact_number,
                    address = address,
                    user = user
                )
            except:
                return JsonResponse({'status': 'error', 'messages': '上传失败'}, status=500)
        #全部写入成功后才提示上传成功
        return JsonResponse({
            'status':'success',
            'messages':'上传成功'
        },status=200)

#学生信息导出
@role_required('admin','teacher')
def export_excel(request):
    if request.method=='POST':
        data=json.loads(request.body)
        grade_id=data.get('grade')
        #判断grade_id是否存在
        if not grade_id:
            return JsonResponse({
                'status':'error',
                'messages':'班级参数缺失'
            },status=400)
        #数据库中判断班级是否存在 不存在则报错
        try:
            grade=Grade.objects.get(id=grade_id)
        except Grade.DoesNotExist:
            return JsonResponse({
                'status':'error',
                'messages':'班级不存在'
            },status=404)
        
        #从数据库查询学生数据
        students=Student.objects.filter(grade=grade)
        if not students.exists():
            return JsonResponse({
                'status':'error',
                'messages':'找不到指定班级学生'
            },status=404)
        #操作excel
        wb=openpyxl.Workbook()
        ws=wb.active
        #添加标题行
        columns = ['班级', '姓名', '学号', '性别', '出生日期', '联系电话', '家庭住址']
        ws.append(columns)
        for student in students:
            if student.gender=='M':
                student.gender='男'
            else:
                student.gender='女'
                #追加后续学生信息
                ws.append([student.grade.grade_name, student.student_name, student.student_number, student.gender, student.birthday, student.contact_number, student.address])

        #将excel数据保存到内存
        excel_file=BytesIO()
        wb.save(excel_file)
        wb.close()
        #重置文件指针位置
        excel_file.seek(0)

        #设置响应
        response = HttpResponse(excel_file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        #以附件形式下载
        response['Content-Disposition'] = 'attachment; filename="students.xlsx"'
        return response
    
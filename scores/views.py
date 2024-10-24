from io import BytesIO
import json
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.generic import ListView,CreateView,UpdateView,DeleteView,DetailView
from django.urls import reverse_lazy
from django.db.models import Q
from pathlib import Path
import openpyxl
from utils.permissions import RoleRequiredMixin, role_required



from grades.models import Grade
from scores.forms import ScoreForm
from scores.models import Score
from students.models import Student
from utils.handle_excel import ReadExcel



# Create your views here.

class BaseScoreView(RoleRequiredMixin):
    model = Score
    success_url = reverse_lazy('score_list')  # 创建成功后重定向的URL
    allowed_roles=['admin','teacher']

#学生成绩查询
class ScoreListView(BaseScoreView,ListView):
    model=Score
    #前台页面路径
    template_name='scores/scores_list.html'
    #展示给前端的数据
    context_object_name='scores'
    success_url=reverse_lazy('score_list')
    paginate_by=10

    def get_context_data(self):
        context=super().get_context_data()
        context['grades']=Grade.objects.all().order_by('grade_number')
        context['current_grade']=self.request.GET.get('grade','')
        return context
    #查询方法
    def get_queryset(self):
        queryset=super().get_queryset()
        #获取搜索内容
        keyword=self.request.GET.get('search')
        #获取班级
        grade_id=self.request.GET.get('grade')
        if grade_id:
            queryset=queryset.filter(grade__pk=grade_id)
        if keyword:
            #根据姓名学号搜索
            queryset=queryset.filter(
                Q(student_name__icontains=keyword)|
                Q(student_number__icontains=keyword)
            )
        return queryset

#学生成绩创建
class ScoreCreateView(BaseScoreView,CreateView):
    form_class=ScoreForm
    template_name = 'scores/score_form.html'

    def form_valid(self,form):
         #从表单获取用户信息
        student_name=form.cleaned_data.get('student_name')
        student_number=form.cleaned_data.get('student_number')
        grade_id=form.cleaned_data.get('grade')

        #查询学生表
        try:
            student=Student.objects.get(
                student_name=student_name,
                student_number=student_number,
                grade=grade_id
            )
        except Student.DoesNotExist:
            errors={'general': [{'message': '学生信息不存在', 'code': 'not_found'}]}
            return JsonResponse({
                "status":"error",
                "messages":errors
            },status=400)
        #保存form实例
        form.save()
        #返回json
        return JsonResponse({
            'status': 'success',
            'messages': '操作成功',
        })
#学生信息编辑
class ScoreUpdateView(BaseScoreView,UpdateView):
    form_class=ScoreForm
    template_name='scores/score_form.html'

    def form_valid(self,form):
        form.save()
        return JsonResponse({
            "status":"success",
            "messages":"操作成功"
        })
    def form_invalid(self,form):
        # 返回错误信息
        errors = {field: [{'message': error, 'code': ''} for error in errors_list] for field, errors_list in form.errors.items()}
        return JsonResponse({'status': 'error', 'messages': errors}, status=400)

#学生成绩删除
class ScoreDeleteView(BaseScoreView,DeleteView):
    def delete(self,request,*args,**kwargs):
        #检查是否为ajax请求
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            response = super().delete(request, *args, **kwargs)
            if response.status_code==302:
                return JsonResponse({
                    "status":"success",
                    "messages":"该成绩已经删除"
                })
            else:
                return JsonResponse({
                    "status":"error",
                    "messages":"删除失败"
                },status=400)
        else:
            return super().delete(request, *args, **kwargs)
#学生成绩查看
class ScoreDetailView(DetailView):
    model=Score
    template_name='scores/score_detail.html'

#学生成绩批量删除
class ScoreBulkDeleteView(BaseScoreView,DeleteView):
    success_url=reverse_lazy('scores_list')
    model=Score
    
    def post(self, request: HttpRequest, *args, **kwargs):
        #获取前台提交的要删除的学生列表
        selected_ids=request.POST.getlist('score_ids')
        #列表为空则返回提示
        if not selected_ids:
            return JsonResponse({
                "status":"error",
                "messages":"请选择要删除的学生成绩信息"
            },status=400)
        #获取所有id在seleted_ids中的成绩信息
        self.object_list=self.get_queryset().filter(id__in=selected_ids)

        try:
            self.object_list.delete()
            return JsonResponse({
                "status":"success",
                "messages":"删除成功"
            },status=200)
        except Exception as e:
            return JsonResponse({
                "status":"error",
                "messages":"删除失败"+str(e)
            },ttatus=500)
#学生成绩导入
@role_required('admin','teacher')
def upload_score(request):
    #上传学生成绩excel文件
    if request.method=='POST':
        #获取文件
        file=request.FILES.get('excel_file')
        #判断文件是否上传
        if not file:
            return JsonResponse({
                'status':'error',
                'messages':'please upload excel_file'
            },status=200)
        #判断文件类型是否为excel suffix:获取后缀
        ext=Path(file.name).suffix
        if ext.lower()!='.xlsx':
            return JsonResponse({
                "status":"error",
                "messages":"文件类型错误，请上传.excel文件"
            },status=400)
        #获取excel数据
        upload=ReadExcel(file)
        data=upload.get_data()
        #获取表头
        if data[0]!=['考试名称','班级','姓名','学号','语文成绩','数学成绩','英语成绩']:
            return JsonResponse({'status':'error','messages':'Excel格式错误'})
        #获取内容数据
        for row in data[1:]:
            title, grade_name, student_name, student_number, chinese_score, math_score, english_score = row
            if not student_name:
                return JsonResponse({'status': 'error', 'messages': '学生姓名不能为空'})
            if not student_number or len(student_number) != 8:
                return JsonResponse({'status': 'error', 'messages': '学籍号不能为空，并且长度应为8位'})
            # 检查班级名称是否存在，已经老师能否上传该班级信息
            grade = Grade.objects.filter(grade_name=grade_name).first()
            if not grade:
                return JsonResponse({'status': 'error', 'messages': f'班级名称"{grade_name}"不存在'})
            
            #判断学生信息是否存在
            try:
                Student.objects.get(
                    student_name=student_name,
                    student_number=student_number,
                    grade=grade
                )
            except Student.DoesNotExist:
                return JsonResponse({'status':'error','messages':'学生信息不存在'})
            
            #在score表中创建记录
            Score.objects.create(
                title=title,
                student_name=student_name,
                student_number=student_number,
                grade=grade,
                chinese_score=chinese_score,
                math_score=math_score,
                english_score=english_score
            )
    return JsonResponse({'status':'success','messages':'upload_success!'})

#学生成绩导出
@role_required('admin','teacher')
def export_excel(request):
    #导出excecl
    if request.method=='POST':
        data=json.loads(request.body)
        grade_id=data.get('grade')
        #判断班级是否存在
        if not grade_id:
            return JsonResponse({
                'status':'error',
                'messages':'班级参数缺失'
            },status=400)
        #判断班级是否存在
        try:
            grade=Grade.objects.get(id=grade_id)
        except Grade.DoesNotExist:
            return JsonResponse({
                'status':'error',
                'messages':'班级不存在'
            },status=404)
        #从数据库查询学生成绩
        scores=Score.objects.filter(grade=grade)
        if not scores.exists():
            return JsonResponse({
                'status': 'error',
                'messages': '找不到指定班级的成绩信息'
                }, status=404)
        #创建Excel工作本
        wb=openpyxl.Workbook()
        ws=wb.active
        ws.title='Score'

        #添加标题行
        columns = ['考试名称', '姓名', '班级', '学号', '语文', '数学', '英语']
        ws.append(columns)

        #填充数据行
        for score in scores:
            ws.append([score.title, score.student_name,score.grade.grade_name, score.student_number, score.chinese_score, score.math_score, score.english_score])
        
        # 将Excel工作簿保存到内存
        excel_file = BytesIO()
        wb.save(excel_file)
        wb.close()

        # 重置文件指针位置
        excel_file.seek(0)

        # 设置响应
        response = HttpResponse(excel_file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="students.xlsx"'
        return response
    
class MyScoreListView(BaseScoreView,ListView):
    model=Score
    template_name='scores/my_score_list.html'
    context_object_name='scores'
    paginate_by=10
    allowed_roles=['admin','teacher','student']

    def get_queryset(self):
        #返回当前用户的成绩
        student_number=self.request.user.student.student_number
        return Score.objects.filter(student_number=student_number)

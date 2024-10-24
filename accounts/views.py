from django.http import JsonResponse
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

from .forms import LoginForm
from students.models import Student
from teachers.models import Teacher

# Create your views here.

#登录功能
def user_login(request):
    #判断是否是post请求
    if request.method == "POST":
        #form表单验证
        form = LoginForm(request.POST)
        #验证失败
        if not form.is_valid():
            return JsonResponse({'status':'error', 'messages': '提交信息有误！'}, status=400, safe=False)
        #验证成功
        username=form.cleaned_data.get('username')
        password=form.cleaned_data.get('password')
        role=form.cleaned_data.get('role')
        #判断角色
        if role=='teacher':
            try:
                #username是表单中提交过来的属性 为老师手机号
                teacher=Teacher.objects.get(phone_number=username)
                #拼接auth_user表中用户名
                username=teacher.teacher_name+'_'+teacher.phone_number
                #authenticate 在auth_user中校验用户存在得方法
                user=authenticate(username=username,password=password)
            except Teacher.DoesNotExist:
                return JsonResponse({'status':'error', 'messages':'老师信息不存在'}, status=404)
        elif role=='student':
            try:
                student = Student.objects.get(student_number=username)
                username = student.student_name + "_" + student.student_number
                user = authenticate(username=username, password=password)
            except:
                return JsonResponse({'status':'error', 'messages':'学生信息不存在'}, status=404)
        else:
            try:
                user = authenticate(username=username, password=password)
            except:
                return JsonResponse({'status':'error', 'messages': '管理员信息不存在'}, status=404)
        #验证成功，即用户存在在auth_user中
        if user is not None:
            #is_active值为1和0 若为1则用户没有被封禁 为0则用户被封禁不能登录
            if user.is_active:
                #登录
                login(request,user)
                #登录成功，将用户名和角色存入session中
                request.session['username']=username.split('_')[0]
                request.session['user_role']=role
                return JsonResponse({'status':'success','messages': '登录成功', 'role': role})
            else:
                return JsonResponse({'status':'error', 'messages': '账户已被禁用'}, status=403)
        else:
            #处理登录失败情况，即auth_user表中没有找到
            return JsonResponse({'status':'error','messages':'用户或密码错误'},status=401)
    #get请求则直接跳到登录页面
    return render(request,'accounts/login.html')

#退出登录
def user_logout(request):
    #第一种退出判断方法
    if 'user_role' in request.session:
        del request.session['user_role']
    logout(request)
    # 第二种 清除所有数据 request.session.flush()
    #重定向到登录页面
    return redirect('user_login')

#修改密码
def change_password(request):
    if request.method=='POST':
        form=PasswordChangeForm(request.user,request.POST)
        if form.is_valid():
            user=form.save()
            update_session_auth_hash(request,user)
            return JsonResponse({
                'status':'success',
                'messages':'your password has been changed'
            })
        else:
            errors=form.errors.as_json()
            return JsonResponse({
                'status':'error',
                'messages':errors
            })
    return render(request,'accounts/change_password.html')
    


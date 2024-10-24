from django.contrib.auth.mixins import AccessMixin
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse_lazy

def role_required(*allowed_roles):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            # 实现验证
            user_role = request.session.get('user_role')
            if request.user.is_authenticated and user_role in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                return JsonResponse({'status': 'error', 'messages': '无权限访问'}, status=403)
        return _wrapped_view
    return decorator

class RoleRequiredMixin(AccessMixin):
    allowed_roles = []

    def dispatch(self, request, *args, **kwargs):
        # 检查是否登录
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        # 检查用户的角色是否允许
        user_role = request.session.get('user_role')
        if not (request.user.is_superuser or user_role in self.allowed_roles):
            return HttpResponseRedirect(reverse_lazy('user_login'))
        
        return super().dispatch(request, *args, **kwargs)
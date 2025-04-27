from django.http import HttpResponseForbidden
from django.conf import settings


class RoleAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 排除管理后台和静态文件
        if request.path.startswith(settings.ADMIN_URL) or \
                request.path.startswith('/static/'):
            return self.get_response(request)

        # 权限检查逻辑
        if not hasattr(request.user, 'role'):
            return HttpResponseForbidden("身份验证异常")

        if request.path.startswith('/instructor/') and \
                not request.user.role == user.Role.INSTRUCTOR:
            return HttpResponseForbidden("讲师权限不足")

        return self.get_response(request)
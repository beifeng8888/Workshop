from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import QA
import requests
import logging

logger = logging.getLogger(__name__)


# 主页面视图（必须保留）
class ChatView(LoginRequiredMixin, TemplateView):
    """
    渲染聊天主界面
    保留TemplateView提供模板渲染能力
    保留LoginRequiredMixin确保登录访问
    """
    template_name = 'chat.html'


# API处理视图
@csrf_exempt
@login_required
def get_ai_response(request):
    """处理AI对话请求的API端点"""
    if request.method != "POST":
        return JsonResponse({'error': '仅接受POST请求'}, status=400)

    try:
        # 获取问题参数（兼容表单格式）
        question = request.POST.get('question', '').strip()
        if not question:
            return JsonResponse({'error': '问题内容不能为空'}, status=400)

        logger.info(f"处理用户问题: {question[:50]}...")

        # 调用DeepSeek API
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": question}],
                "temperature": 0.7,
                "max_tokens": 2000
            },
            timeout=30
        )
        response.raise_for_status()

        # 解析响应
        response_data = response.json()
        ai_answer = response_data['choices'][0]['message']['content']
        logger.info(f"获取AI回答，长度: {len(ai_answer)}")

        # 保存到数据库
        QA.objects.create(
            user=request.user,
            title=question[:50],
            content=question,
            answer=ai_answer,
            is_resolved=False
        )

        return JsonResponse({'answer': ai_answer})

    except requests.exceptions.RequestException as e:
        error_msg = f"API请求失败: {str(e)}"
        logger.error(error_msg)
        return JsonResponse({'error': error_msg}, status=500)

    except Exception as e:
        logger.exception("处理请求时发生未预期异常")
        return JsonResponse({'error': '服务器内部错误'}, status=500)
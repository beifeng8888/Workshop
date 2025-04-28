import json
import threading
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.http import StreamingHttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import QA
import requests
import logging
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

logger = logging.getLogger(__name__)

# 同步保存到数据库的函数
def save_to_db(user, question, answer):
    """同步保存到数据库"""
    try:
        QA.objects.create(
            user=user,
            title=question[:50],
            content=question,
            answer=answer,
            is_resolved=False
        )
        logger.info(f"问题已保存到数据库，长度: {len(answer)}")
    except Exception as e:
        logger.error(f"数据库保存失败: {str(e)}")

class ChatView(LoginRequiredMixin, TemplateView):
    template_name = 'chat.html'

@csrf_exempt
@login_required
def get_ai_response(request):
    """同步处理AI对话请求"""
    if request.method != "POST":
        return JsonResponse({'error': '仅接受POST请求'}, status=400)

    def generate():
        try:
            # 解析请求数据
            try:
                data = json.loads(request.body)
                question = data.get('question', '').strip()
                if not question:
                    yield "data: " + json.dumps({"error": "问题内容不能为空"}) + "\n\n"
                    return
            except Exception as e:
                yield "data: " + json.dumps({"error": f"请求解析失败: {str(e)}"}) + "\n\n"
                return

            # 配置带重试机制的Session
            session = requests.Session()
            retry = Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[500, 502, 503, 504]
            )
            adapter = HTTPAdapter(max_retries=retry)
            session.mount("https://", adapter)

            # 调用DeepSeek API
            try:
                response = session.post(
                    "https://api.deepseek.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
                        "Content-Type": "application/json",
                        "Accept": "text/event-stream"
                    },
                    json={
                        "model": "deepseek-chat",
                        "messages": [{"role": "user", "content": question}],
                        "stream": True,
                        "temperature": 0.7,
                        "max_tokens": 2000
                    },
                    stream=True,
                    timeout=(10, 30)
                )
                response.raise_for_status()

                full_response = ""
                for line in response.iter_lines():
                    if line:

                        decoded = line.decode('utf-8')
                        if decoded == '[DONE]':
                            yield "data: " + json.dumps({"event": "done"}) + "\n\n"
                            continue
                        if decoded.startswith('data:'):
                            yield decoded + "\n\n"
                            try:
                                data = json.loads(decoded[5:])
                                if data.get('choices'):
                                    full_response += data['choices'][0].get('delta', {}).get('content', '')
                            except:
                                pass

                # 同步保存到数据库
                save_to_db(request.user, question, full_response)

            except requests.exceptions.RequestException as e:
                error_msg = f"API请求失败: {str(e)}"
                if isinstance(e, requests.exceptions.Timeout):
                    error_msg = "API响应超时，请稍后重试"
                yield "data: " + json.dumps({"error": error_msg}) + "\n\n"

        except Exception as e:
            yield "data: " + json.dumps({"error": f"服务器内部错误: {str(e)}"}) + "\n\n"

    return StreamingHttpResponse(
        generate(),
        content_type='text/event-stream; charset=utf-8'
    )
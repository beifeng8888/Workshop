from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Tag(models.Model):
    name = models.CharField('标签名', max_length=50, unique=True)

    def __str__(self):
        return self.name


class QA(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='提问用户',
        related_name='QA'
    )
    title = models.CharField('问题描述', max_length=128)
    content = models.TextField('详细描述')
    created_at = models.DateTimeField('提问时间', auto_now=True)
    is_resolved = models.BooleanField('是否解决', default=False)
    tags = models.ManyToManyField('Tag',blank=True)
    answer = models.TextField('答案')

    class Meta:
        verbose_name = '提问'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title:[20]}...{self.user}"


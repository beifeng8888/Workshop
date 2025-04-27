from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    org = models.CharField('组织', max_length=128, blank=True)
    telephone = models.CharField('电话', max_length=50, blank=True)
    mod_date = models.DateTimeField('最后修改时间', auto_now=True)

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name
        permissions = [
            # 格式：(codename, name)
            ('instructor', '讲师权限')
        ]
    def __str__(self):
        return self.username
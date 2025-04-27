from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class Role(models.TextChoices):
    STUDENT = 'ST', '学员'
    INSTRUCTOR = 'IN', '讲师'


class UserManager(BaseUserManager):
    def create_user(self, email, password=None,** extra_fields):
        if not email:
            raise ValueError('必须提供电子邮箱')
        user = self.model(email=self.normalize_email(email),** extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, ** extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password,** extra_fields)

        class User(AbstractUser):
            username = None  # 禁用默认用户名
            email = models.EmailField('邮箱', unique=True)
            role = models.CharField('角色', max_length=2,
                                    choices=Role.choices,
                                    default=Role.STUDENT)
            container_limit = models.PositiveIntegerField('容器配额', default=1)

            USERNAME_FIELD = 'email'
            REQUIRED_FIELDS = []

            objects = UserManager()

            class Meta:
                permissions = [
                    ("access_dashboard", "Can access instructor dashboard"),
                ]
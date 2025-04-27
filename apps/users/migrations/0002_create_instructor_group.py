from django.db import migrations


def create_instructor_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')

    # 创建讲师组
    group, _ = Group.objects.get_or_create(name='Instructor Group')

    # 获取自定义权限
    permissions = Permission.objects.filter(
        codename__in=['instructor']
    )
    group.permissions.add(*permissions)


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0001_initial'),  # 指向包含自定义权限的迁移
    ]

    operations = [
        migrations.RunPython(create_instructor_group),
    ]
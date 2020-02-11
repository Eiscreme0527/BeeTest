import jwt
from django.db import models
from BeeTest import settings
from datetime import datetime, timedelta
from django.contrib.auth.models import User, AbstractBaseUser, PermissionsMixin, BaseUserManager


class UserManager(BaseUserManager):
    def _create_user(self, username, password, email, **kwargs):
        if not username:
            raise ValueError("pls input user name.")
        if not password:
            raise ValueError("pls input password.")
        if not email:
            raise ValueError("pls input email address.")

        user = self.model(username=username, email=email, **kwargs)
        user.set_password(password)
        user.save()
        return user

    def create_user(self, username, password, email, **kwargs):
        kwargs['is_superuser'] = False
        return self._create_user(username, password, email, **kwargs)

    def create_superuser(self, username, password, email, **kwargs):
        kwargs['is_superuser'] = True
        kwargs['is_staff'] = True
        return self._create_user(username, password, email, **kwargs)


class Member(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(unique=True, max_length=11, verbose_name='用户名')
    real_name = models.CharField(max_length=20, verbose_name='真实姓名')
    password = models.CharField(max_length=48, verbose_name='密码')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='添加时间')
    phone = models.CharField(max_length=11, verbose_name='手机号')
    account_type_choice = ((1, "普通账户"), (2, "高级账户"), (3, "超级账户"),
                           (4, "管理账户"))
    account_type = models.IntegerField(choices=account_type_choice, default=1,
                                       verbose_name='账号类型')
    update_time = models.DateTimeField(auto_now=True, verbose_name='修改时间', blank=True, null=True)
    login_time = models.DateTimeField(verbose_name='登录时间', auto_now=True, blank=True)
    last_login_time = models.DateTimeField(verbose_name='上次登录时间', auto_now=False, blank=True,
                                           default=datetime.utcnow())
    account_status_choice = ((1, "正常"), (2, "冻结"), (3, "删除"))
    account_status = models.IntegerField(choices=account_status_choice, default=1,
                                         verbose_name='账户状态')
    is_active = models.BooleanField(default=True, verbose_name='激活状态')
    email = models.EmailField(verbose_name='邮箱', blank=True)
    integral = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='积分', blank=True, default=0.00)
    exp_time = models.DateTimeField(verbose_name='Token过期时间', auto_now=False, blank=True,
                                    default=datetime.utcnow() + timedelta(days=1))

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['phone']

    def __str__(self):
        return self.username

    @property
    def token(self):
        return self._generate_jwt_token()

    def _generate_jwt_token(self):
        exp = datetime.utcnow() + timedelta(days=1)
        token = jwt.encode({
            'exp': exp,
            'iat': datetime.utcnow(),
            'data': {
                'username': self.username
            }
        }, settings.SECRET_KEY, algorithm='HS256')
        lt = self.login_time
        nt = datetime.utcnow()
        # print("exp=", exp)
        self.exp_time = exp
        self.last_login_time = lt
        self.login_time = nt
        self.save()

        return token.decode('utf-8')

    class Meta:
        default_permissions = ()

        permissions = (
            ("test_case_manage ", "can manage test case"),
            ("task_call_manage", "can manage task call"),
            ("user_manage", "can manage user"),
            ("event_manage", "can manage event"),
            ("report_form_manage", "can manage report form"),
            ("notice_manage", "can manage notice"),
            ("device_manage", "can manage device"),
            ("log_manage", "can manage log"),
        )
        verbose_name = '用户'
        verbose_name_plural = '用户'

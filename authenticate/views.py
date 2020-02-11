import hashlib
import requests
import datetime
import random
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from django.shortcuts import render, HttpResponse
from authenticate.models import Member
from django.http import JsonResponse
from django.contrib import auth
from authenticate.utils import auth_permission_required, get_user


def get_valid_img(request):
    # generate random color.
    def get_random_color(is_light=True):
        return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)

    # generate background picture.
    img = Image.new('RGB', (120, 50), get_random_color())
    # use brush.
    draw = ImageDraw.Draw(img)
    # set captcha's font.
    font = ImageFont.truetype('arial.ttf', 36)
    # create a variable to store the captcha string.
    captcha_text = ''
    # generate captcha(include digits and upper lower letters.)
    for i in range(5):
        random_num = str(random.randint(0, 9))
        random_lower_char = chr(random.randint(97, 122))
        random_upper_char = chr(random.randint(65, 90))
        random_text = random.choice([random_num, random_lower_char, random_upper_char])
        draw.text((i * 20 + 10, 5), random_text, get_random_color(), font)
        captcha_text += random_text

    # generate interference line and hot pixel.
    width = 130
    height = 40
    for i in range(10):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        draw.line((x1, y1, x2, y2), fill=get_random_color())
    for i in range(120):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        draw.point((x1, y1), fill=get_random_color())

    # set session.
    request.session['captcha_text'] = captcha_text
    print(captcha_text)

    # store the generated picture in memory.
    bug = BytesIO()
    img.save(bug, 'png')

    # return captcha picture.
    return HttpResponse(bug.getvalue(), 'image/png')


# def login1(request):
#     res = {'status': 1, 'err': '',
#            'data': {'is_success': False, "token": "",
#                     'last_login_time': '', 'login_time': '', 'exp_time': ''}}
#
#     if request.method == 'POST':
#         phone = request.POST.get("phone")
#         pwd = request.POST.get("password")
#
#         print(phone, pwd)
#         if not phone:
#             res["err"] = "请输入手机号"
#             return JsonResponse(res)
#         if not pwd:
#             res["err"] = "请输入密码"
#             return JsonResponse(res)
#         try:
#             user = Member.objects.get(username=phone)
#         except Member.DoesNotExist:
#             res["err"] = "用户不存在"
#             return JsonResponse(res)
#
#         if user:
#             if user.account_status == 1:
#                 print(user.email)
#                 # p = sha1_encode(pwd)
#                 if pwd != user.password:
#                     res["err"] = "用户名密码错误"
#                     return JsonResponse(res)
#                 else:
#                     res["msg"] = "登录成功"
#                     res["data"]["is_success"] = True
#                     # 调用user.token会创建token
#                     res["data"]["token"] = user.token
#                     res["data"]["last_login_time"] = user.last_login_time
#                     res["data"]["login_time"] = user.login_time
#                     res["data"]["exp_time"] = user.exp_time
#                     return JsonResponse(res)
#             res["err"] = "用户不存在"
#             return JsonResponse(res)
#         else:
#             res["err"] = "用户不存在"
#             return JsonResponse(res)
#
#     else:
#         res["err"] = "请求方式错误"
#         return JsonResponse(res)


@auth_permission_required('authenticate.task_1call_manage')
def info(request):
    if request.method == 'GET':
        json_data = {
            "user": "daibing",
            "email": "yyxzz0527@yeah.net"
        }

        return JsonResponse({"state": 1, "message": json_data})
    else:
        return JsonResponse({"state": 0, "message": "Request method 'POST' not supported"})


@auth_permission_required('BeeTest.change_user')
def update(req):
    res = {'status': 1, 'err': '', 'data': {'is_success': False}}
    if req.method == 'POST':
        username = req.POST.get("username")
        phone = req.POST.get("phone")
        QQ = req.POST.get("QQ")
        email = req.POST.get("email")
        WeChart = req.POST.get("WeChart")
        birthday = req.POST.get("birthday")
        update_time = datetime.datetime.utcnow()

        user = get_user(req)

        try:
            user.update(username=username, phone=phone, QQ=QQ,
                        email=email, WeChart=WeChart, birthday=birthday,
                        update_time=update_time)
            user.save()

            res["msg"] = "修改成功"
            res["data"]["is_success"] = True
            return JsonResponse(res)

        except Exception as e:
            print(e)
            res["err"] = "修改失败"
            return JsonResponse(res)

    else:
        res["err"] = "请求方式错误"
        return JsonResponse(res)


def index(request):
    return render(request, "login.html")


# view of login
def login(request):
    response = {'status': 1, 'error': '',
                'data': {'is_success': False, "token": "",
                         'last_login_time': '', 'login_time': '', 'exp_time': ''}}
    # Judge request mode
    if request.is_ajax():
        # Get front-end data
        user = request.POST.get('user')
        password = request.POST.get('password')
        captcha = request.POST.get('captcha')
        # Create response data dictionary
        # response = {"user": None, "error": ""}
        if not user:
            response['status'] = 0
            response['error'] = 'please entry username'
            return JsonResponse(response)
        if not password:
            response['status'] = 0
            response['error'] = 'please entry password'
            return JsonResponse(response)
        if not captcha:
            response['status'] = 0
            response['error'] = 'please entry captcha'
            return JsonResponse(response)

        # Whether the captcha-code is consistent
        if captcha.upper() == request.session.get('captcha_text').upper():
            # If captcha-code verified through then return user object
            # user_obj = auth.authenticate(username=user, password=password)
            try:
                user_obj = Member.objects.get(username=user)
            except Member.DoesNotExist:
                response['error'] = 'user not exist'
                return JsonResponse(response)
            if user_obj:
                if user_obj.account_status == 1:
                    print(user_obj.token)
                    if password != user_obj.password:
                        response['error'] = 'password is valid'
                        return JsonResponse(response)
                    else:
                        response["msg"] = "login success"
                        response["data"]["is_success"] = True
                        # 调用user.token会创建token
                        response["data"]["token"] = user_obj.token
                        response["data"]["last_login_time"] = user_obj.last_login_time
                        response["data"]["login_time"] = user_obj.login_time
                        response["data"]["exp_time"] = user_obj.exp_time
                        return JsonResponse(response)
            else:
                response['status'] = 0
                response['error'] = 'user not exist'
                return JsonResponse(response)

        else:
            response['user'] = 'captcha error'
            return JsonResponse(response)

    else:
        response["err"] = "request mode error"
        return render(request, 'login.html')

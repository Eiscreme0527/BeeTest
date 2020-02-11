import jwt 
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from authenticate.models import Member

UserModel = get_user_model()


def auth_permission_required(perm):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            # formatted authorities.
            perms = (perm,) if isinstance(perm, str) else perm
            print(perms, perm)  # ('authenticate.can manage test case',) authenticate.can manage test case
            print(request.user.is_authenticated)  # False
            if request.user.is_authenticated:
                # determine the authority of the successful login user.
                if not request.user.has_perms(perms):
                    raise PermissionDenied
            else:
                try:
                    auth = request.META.get('HTTP_AUTHORIZATION').split()
                    print(auth)  # token
                except AttributeError:
                    return JsonResponse({"code": 401, "message": "No authenticate header"})

                # through API to get data, then execute validation process.
                if auth[0].lower() == 'token':
                    try:
                        dict = jwt.decode(auth[1], settings.SECRET_KEY, algorithms=['HS256'])
                        username = dict.get('data').get('username')
                        print(username)  # 13641111185
                    except jwt.ExpiredSignatureError:
                        return JsonResponse({"status_code": 401, "message": "Token expired"})
                    except jwt.InvalidTokenError:
                        return JsonResponse({"status_code": 401, "message": "Invalid token"})
                    except Exception as e:
                        return JsonResponse({"status_code": 401, "message": "Can not get user object"})

                    try:
                        user = UserModel.objects.get(username=username)
                        print(user)  # 13641111185
                    except UserModel.DoesNotExist:
                        return JsonResponse({"status_code": 401, "message": "User Does not exist"})

                    if not user.is_active:
                        print(user.is_active)
                        return JsonResponse({"status_code": 401, "message": "User inactive or deleted"})
                    print(perm)  # authenticate.can manage test case
                    print(user.has_perms(perm))  # True

                    # determine the authority of the successful login user by token.
                    if not user.has_perms(perms):
                        print(perms)
                        return JsonResponse({"status_code": 403, "message": "PermissionDenied"})
                else:
                    return JsonResponse({"status_code": 401, "message": "Not support auth type"})

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


def get_user(req):
    auth = req.META.get('HTTP_AUTHORIZATION').split()
    dict = jwt.decode(auth[1], settings.SECRET_KEY, algorithms=['HS256'])
    username = dict.get('data').get('username')
    try:
        user = Member.objects.get(username=username)
        print(user)
    except Member.DoesNotExist:
        return JsonResponse({'status': 0, 'err': "user not exist"})

    return user

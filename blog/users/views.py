import re
from asyncio.log import logger

from django.contrib.auth import login, authenticate, logout
from django.db import DatabaseError
from django.shortcuts import render, redirect
from django.http.response import HttpResponseBadRequest, JsonResponse
from django.template import response
from django.urls import reverse
from home.models import ArticleCategory
from libs.captcha.captcha import captcha
from django_redis import get_redis_connection
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from home.models import ArticleCategory,Article

# Create your views here.

# 注册视图
from django.views import View

# 注册视图
from users.models import User


class RegisterView(View):
    def get(self, request):
        return render(request, "register.html")

    def post(self, request):
        # 1.接收数据
        mobile = request.POST.get("mobile")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")
        imgage_code = request.POST.get("imgage_code").upper()
        uuid = request.POST.get("uuid")
        # 2.验证数据
        #     2.1 参数是否安全
        if not all([mobile, password, password2]):
            return HttpResponseBadRequest("缺少必要的参数！")
        #     2.2 手机号的格式是否正确
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return HttpResponseBadRequest("手机号不符合规则！")
        #     2.3 密码是否符合格式
        if not re.match(r"^[0-9A-Za-z]{8,20}$", password):
            return HttpResponseBadRequest("请输入8-20为密码，密码是数字，字母！")
        #     2.4 密码和确认密码是否一致
        if password != password2:
            return HttpResponseBadRequest("两次输入密码不一致！")
        #     2.5 验证码是否要一致
        redis_conn = get_redis_connection('default')
        img_code_server = redis_conn.get('img:%s' % uuid)
        if img_code_server is None:
            return HttpResponseBadRequest('图片验证码已过期')
        if imgage_code != img_code_server.decode():
            return HttpResponseBadRequest('图片验证码错误')
        # 3.保存注册信息
        # create_user 可以使用系统的方法来对密码进行加密
        try:
            user = User.objects.create_user(username=mobile,
                                            mobile=mobile,
                                            password=password)
        except DatabaseError as e:
            logger.error(e)
            return HttpResponseBadRequest("注册失败")
        # 4.返回相应跳转到指定页面
        # redirect 进行重定向
        # reverse 可以通过 namespace:namespace 来获取到视图所对应的路由
        response = redirect(reverse("home:index"))

        # login() 登录状态保持
        login(request, user)

        # 设置cookie信息，方便 首页中 用户信息的展示和判断
        response.set_cookie("is_login", True)
        response.set_cookie("username", user.username, max_age=7 * 24 * 3600)
        return response


class ImageCodeView(View):
    def get(self, request):
        # 1.接收前端传递过来的uuid
        uuid = request.GET.get('uuid')
        # 2.判断uuid是否获取到
        if uuid is None:
            return HttpResponseBadRequest('没有传递UUID')
        # 3.通过调用captcha来乘车图片验证码
        text, image = captcha.generate_captcha()
        # 4.将图片内容保存到redis中
        redis_connection = get_redis_connection()
        #         uuid作为一个key，图片内容作为一个value，同时我们还需要设置一个时效
        # key设置为uuid
        # seconds 过期秒数  300秒  5 分钟过期时间
        # value  text
        redis_connection.setex("img:%s" % uuid, 300, text);
        # 5. 返回图片二进制
        return HttpResponse(image, content_type="image/jpeg")


class LoginView(View):
    def get(self, request):
        return render(request, "login.html")

    def post(self, request):
        # 1.接收参数
        mobile = request.POST.get("mobile")
        password = request.POST.get("password")
        remember = request.POST.get("remember")
        # 2.参数的验证
        #     2.1 验证手机号
        if not re.match(r'^[a-zA-Z0-9]{8,20}$', mobile):
            return HttpResponseBadRequest("手机号不符合规则")
        #     2.2 验证密码是否符合规则
        if not re.match(r'^[a-zA-Z0-9]{8,20}$', password):
            return HttpResponseBadRequest("密码不符合规则")
        # 3.用户认证登录
        # 采用系统自带的认证方法进行认证
        # 如果我们的用户名和密码正确，会返回user
        # 如果我们的用户名或密码不正确,会返回None
        # 默认的认证的方法 针对于username字段进行用户名的判断
        # 当前的判断信息是  手机号,索引我们需要修改一下认证字段
        user = authenticate(mobile=mobile, password=password)
        # 4.状态的保持
        login(request, user)
        # 5.根据用户选择的是否记住登录状态来进行判断

        # 根据next参数来进行页面的跳转
        next_page = request.GET.get("next")
        if next_page:
            response = redirect(next_page)
        else:
            response = redirect(reverse('home:index'))

        if remember != 'on':  # 没有记住用户信息
            # 浏览器关闭后
            request.session.set_expiry(0)
            # 6.为了首页显示我们需要设置一些cookie信息
            response.set_cookie("is_login", True)
            response.set_cookie("username", user.username, max_age=14 * 24 * 3600)
        else:  # 记住用户信息  过期时间2周
            request.session.set_expiry(None)
            response.set_cookie('is_login', True, max_age=14 * 24 * 3600)
            response.set_cookie("username", user.username, max_age=14 * 24 * 3600)
        # 7. 返回相应
        return response


class LogoutView(View):
    def get(self,request):
        # 1. session数据清除
        logout(request)
        # 2. 删除部分cookie数据
        response=redirect(reverse('home:index'))
        response.delete_cookie("is_login")
        # 3.跳转到首页
        return response


# LoginRequiredMixin
# 如果用户未登录的话,则会进行默认的跳转
# 默认的跳转连接是: accounts/login/?next/center
class UserCenterView(LoginRequiredMixin,View):
    def get(self,request):
        # 获取登录用户的信息
        user = request.user
        # 组织获取用户的信息
        context = {
            'username': user.username,
            'mobile': user.mobile,
            'avatar': user.avatar.url if user.avatar else None,
            'user_desc':user.user_desc
        }
        return render(request,"center.html",context=context)

    def post(self, request):
        user = request.user
        # 1.接收参数
        username = request.POST.get("username",user.username)
        user_desc = request.POST.get('desc',user.user_desc)
        avatar = request.FILES.get("avatar")
        # 2.将参数保存起来
        try:
            user.username = username
            user.user_desc = user_desc
            if avatar:
                user.avatar = avatar
            user.save()
        except Exception as e:
            logger.error(e)
            return HttpResponseBadRequest("修改失败,请稍后再试")
        # 3.更新cookie中的username信息

        # 4.刷新当前页面(重定向操作)
        response = redirect(reverse("users:center"))
        response.set_cookie("username",user.username,max_age=14*3600*24)
        # 5. 返回相应
        return response


class WriteBlogView(LoginRequiredMixin,View):

    def get(self,request):
        #查询所有分类模型
        categories=ArticleCategory.objects.all()

        context = {
            'categories':categories
        }
        return render(request,'write_blog.html',context=context)

    def post(self,request):
        """
        # 1.接收数据
        # 2.验证数据
        # 3.数据入库
        # 4.跳转到指定页面（暂时首页）
        :param request:
        :return:
        """
        # 1.接收数据
        avatar=request.FILES.get('avatar')
        title=request.POST.get('title')
        category_id=request.POST.get('category')
        tags=request.POST.get('tags')
        sumary=request.POST.get('sumary')
        content=request.POST.get('content')
        user=request.user

        # 2.验证数据
        # 2.1 验证参数是否齐全
        if category_id == 'none':
            return HttpResponseBadRequest('参数不全')
        if not all([avatar,title,category_id,sumary,content]):
            return HttpResponseBadRequest('参数不全')
        # 2.2 判断分类id
        try:
            category=ArticleCategory.objects.get(id=category_id)
        except ArticleCategory.DoesNotExist:
            return HttpResponseBadRequest('没有此分类')
        # 3.数据入库
        try:
            article=Article.objects.create(
                author=user,
                avatar=avatar,
                title=title,
                category=category,
                tags=tags,
                sumary=sumary,
                content=content
            )
        except Exception as e:
            logger.error(e)
            return HttpResponseBadRequest('发布失败，请稍后再试')
        # 4.跳转到指定页面（暂时首页）
        return redirect(reverse('home:index'))

# 删除博客
class DeleteBlogView(LoginRequiredMixin,View):
    def get(self,request):
        # 获取登录用户的信息
        user = request.user
        # 获取删除博客id
        articleID = request.GET.get('articleID')
        # 数据入库
        try:
            Article.objects.get(id=articleID).delete()
        except Exception as e:
            logger.error(e)
            return HttpResponseBadRequest('删除博客失败，请稍后再试')
        # 4.跳转到指定页面（暂时首页）
        return redirect(reverse('home:index'))


# 重置密码
class ResetPasswordView(LoginRequiredMixin,View):
    def get(self,request):
        user = request.user
        # 组织获取用户的信息
        context = {
            'username': user.username,
            'mobile': user.mobile,
            'avatar': user.avatar.url if user.avatar else None,
            'user_desc': user.user_desc
        }
        return render(request,"reset_password.html", context=context)
    def post(self,request):
        # 1.读取数据
        mobile = request.POST.get("mobile")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")
        imgage_code = request.POST.get("imgage_code").upper()
        uuid = request.POST.get("uuid")
        # 2判断参数是否齐全
        if not all([mobile, password, password2]):
            return HttpResponseBadRequest('缺少必传参数')
        # 判断手机号是否合法
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return HttpResponseBadRequest('请输入正确的手机号码')
        # 判断密码是否是8-20个数字
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return HttpResponseBadRequest('请输入8-20位的密码')
        # 判断两次密码是否一致
        if password != password2:
            return HttpResponseBadRequest('两次输入的密码不一致')
        #  验证码是否要一致
        redis_conn = get_redis_connection('default')
        img_code_server = redis_conn.get('img:%s' % uuid)
        if img_code_server is None:
            return HttpResponseBadRequest('图片验证码已过期')
        if imgage_code != img_code_server.decode():
            return HttpResponseBadRequest('图片验证码错误')
        # 3.根据手机号查询数据
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            return HttpResponseBadRequest('修改失败，请稍后再试')
        else:
            # 修改用户密码
            user.set_password(password)
            user.save()

        # 跳转到登录页面
        response = redirect(reverse('users:login'))

        return response
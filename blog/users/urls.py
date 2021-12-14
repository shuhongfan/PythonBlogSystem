"""
@Time ： 2021/12/12 14:52
@Auth ： 021321752215舒洪凡
@File ：urls.py
@IDE ：PyCharm
"""

# 进行users子应用的视图路由
from django.urls import path
from users.views import RegisterView, ImageCodeView, LoginView, LogoutView, UserCenterView, WriteBlogView, \
    ResetPasswordView, DeleteBlogView

urlpatterns = [
    # path的路由
    #     第一个参数: 路由
    #     path的第二个参数: 视图函数名
    path('register/',RegisterView.as_view(),name='register'),

    # 图片验证码的路由
    path('imagecode/',ImageCodeView.as_view(),name='imagecode'),

    # 登录路由
    path("login/",LoginView.as_view(),name="login"),

    # 退出登录
    path("logout/",LogoutView.as_view(),name="logout"),

    # 个人中心
    path("center/",UserCenterView.as_view(),name="center"),

    # 写博客的路由
    path("writeblog/",WriteBlogView.as_view(),name="writeblog"),

    # 删除博客
    path("deleteblog/",DeleteBlogView.as_view(),name="deleteblog"),

    # 重置密码
    path("resetpassword/",ResetPasswordView.as_view(),name="resetpassword")
]
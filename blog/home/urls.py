"""
@Time ： 2021/12/12 20:10
@Auth ： 021321752215舒洪凡
@File ：urls.py
@IDE ：PyCharm
"""
from django.urls import path
from home.views import IndexView, DetailView

urlpatterns = [
    # 首页的路由
    path("",IndexView.as_view(),name='index'),
    # 详情视图的路由
    path('detail/',DetailView.as_view(),name='detail')
]

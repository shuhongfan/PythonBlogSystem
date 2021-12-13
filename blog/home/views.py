from django.http import HttpResponseNotFound
from django.shortcuts import render

# Create your views here.
from django.views import View


class IndexView(View):
    def get(self,request):
        # # 1. 获取所有分类信息
        # categories = ArticleCategory.objects.all()
        # # 2.接收用户点击的分类id
        # cat_id = request.GET.get('cat_id',1)
        # # 3.根据分类id进行分类的查询
        # try:
        #     category = ArticleCategory.objects.all(id=cat_id)
        # except ArticleCategory.DoesNotExist:
        #     return HttpResponseNotFound("没有此分类")
        # # 4.组织数据传递给模板
        # context = {
        #     'categories': categories,
        #     'category': category
        # }
        return render(request, 'index.html')
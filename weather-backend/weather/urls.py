"""
URL configuration for weather project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path


"""
path
- route: 路由路径
- view: 对应的view视图，传入HttpRequest作为第一个参数
- kwargs
- name: URL 取名能使你在 Django 的任意地方唯一地引用它

"""
urlpatterns = [

    path('admin/', admin.site.urls),
    path("api/", include("api.urls")),
]


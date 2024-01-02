from django.contrib import admin

# Register your models here.
from django.contrib import admin

from .models import RealData, HistoryData

admin.site.register(RealData)
admin.site.register(HistoryData)
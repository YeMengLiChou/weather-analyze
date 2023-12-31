import scrapy
from django.db import models


# Create your models here.

class RealData(models.Model):
    city_name = models.CharField(max_length=20, )
    city_id = models.CharField(max_length=20, primary_key=True)
    city_province = models.CharField(max_length=20)
    temp = models.DecimalField(decimal_places=1, max_digits=5)
    d_temp = models.DecimalField(decimal_places=1, max_digits=5)
    n_temp = models.DecimalField(decimal_places=1, max_digits=5)
    humidity = models.IntegerField()
    w_direction = models.CharField(max_length=10)
    w_level = models.IntegerField()
    w_speed = models.IntegerField()
    rain = models.DecimalField(decimal_places=1, max_digits=5)
    rain24h = models.DecimalField(decimal_places=1, max_digits=5)
    aqi = models.IntegerField()
    description = models.CharField(max_length=15)
    content = models.CharField(max_length=1500)
    timestamp = models.DateTimeField()
    sunrise = models.DateTimeField()
    sunset = models.DateTimeField()

    def __str__(self):
        return f"{self.city_name} {self.timestamp} {self.temp}"


class HistoryData(models.Model):
    # 城市中文 str
    city_name = models.CharField(max_length=20, )
    # 城市id str/int
    city_id = models.CharField(max_length=20)
    # 城市所属省份 str
    city_province = models.CharField(max_length=20)
    # 当前时间的时间戳 timestamp
    timestamp = models.DateTimeField()
    # 天气描述 str
    description = models.CharField(max_length=10)
    # 最高温度 int
    high_temp = models.IntegerField()
    # 最低温度 int
    low_temp = models.IntegerField()
    # 风向 str
    w_direction = models.CharField(max_length=10)
    # 风等级 str
    w_level = models.CharField(max_length=10)
    # aqi int
    aqi = models.IntegerField(null=True)
    # aqi状态 str
    aqi_status = models.CharField(max_length=10, null=True)

    def __str__(self):
        return f"{self.city_name} {self.timestamp} {self.description}"

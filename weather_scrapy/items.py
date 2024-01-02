import scrapy


class RealWeatherItem(scrapy.Item):
    """
    实时数据Item
    """
    # 城市中文 str
    city_name = scrapy.Field()
    # 城市id str/int
    city_id = scrapy.Field()
    # 城市所属省份中文  str
    city_province = scrapy.Field()

    # 当前温度 float
    temp = scrapy.Field()
    # 白天温度 float
    d_temp = scrapy.Field()
    # 夜晚温度 float
    n_temp = scrapy.Field()
    # 湿度 float %
    humidity = scrapy.Field()
    # 风向 str
    w_direction = scrapy.Field()
    # 风级 str
    w_level = scrapy.Field()
    # 风速 int
    w_speed = scrapy.Field()
    # 降水量 int
    rain = scrapy.Field()
    # 24小时降水量 int
    rain24h = scrapy.Field()
    # 空气质量 str
    aqi = scrapy.Field()
    # 天气描述 str
    description = scrapy.Field()
    # 生活指数表述 str
    content = scrapy.Field()
    # 时间戳 timestamp / int
    timestamp = scrapy.Field()
    # 日出日落时间 timestamp / int
    sunrise = scrapy.Field()
    sunset = scrapy.Field()


class HistoryWeatherItem(scrapy.Item):
    # 城市中文 str
    city_name = scrapy.Field()
    # 城市id str/int
    city_id = scrapy.Field()
    # 城市所属省份 str
    city_province = scrapy.Field()
    # 当前时间的时间戳 timestamp
    timestamp = scrapy.Field()
    # 天气描述 str
    description = scrapy.Field()
    # 最高温度 int
    high_temp = scrapy.Field()
    # 最低温度 int
    low_temp = scrapy.Field()
    # 风向 str
    w_direction = scrapy.Field()
    # 风等级 str
    w_level = scrapy.Field()
    # aqi int
    aqi = scrapy.Field()
    # aqi状态 str
    aqi_status = scrapy.Field()



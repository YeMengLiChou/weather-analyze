# 统计数据

1. 累年的各月极端气温（最高和最低气温）
2. 累年来的各月平均降水量
3. 累年来的各月最大降水量
4. 累年来的各月平均气氛、平均最高低温
5. 累年来的各月平均气温

天气词条分析：

- 词云显示

- 柱状图显示

- 饼图分布显示

  ![image-20231228155127197](./.assets/Python%E5%A4%A7%E4%BD%9C%E4%B8%9A/image-20231228155127197.png)

风向：

![image-20231228155039520](./.assets/Python%E5%A4%A7%E4%BD%9C%E4%B8%9A/image-20231228155039520.png)

温湿度分析

![image-20231228155238210](./.assets/Python%E5%A4%A7%E4%BD%9C%E4%B8%9A/image-20231228155238210.png)

实况最高温度比较

![image-20231228160330734](./.assets/Python%E5%A4%A7%E4%BD%9C%E4%B8%9A/image-20231228160330734.png)

# 爬取网站

http://www.weather.com.cn/weather1d

天气预报的数据

- 温度，天气、风级、湿度

实时和预报











# 流程

## 爬虫

首先要确定要爬取什么数据：

- 哪些城市的数据：每个省下面的市级城市
- 什么时间的数据：历史数据以及当前时间的数据，还有7天预测的数据
- 爬取什么数据：温度、风向、天气描述



https://tianqi.2345.com/wea_history/：用于爬取历史数据

http://www.weather.com.cn/：用于爬取当前数据以及未来7天的数据



### 城市关系

https://tianqi.2345.com/tqpcimg/tianqiimg/theme4/js/citySelectData2.js可以获取所有市级城市

https://tianqi.2345.com/tqpcimg/tianqiimg/theme4/js/global.js?v=20220613可以获取所有省级城市

通过解析上面两个文件来构建城市

- 将爬取到的数据保存到redis中，确保仅爬取一次！



保存到 redis 的格式为：（前缀为 `city:info:_id`)

1. 第一种

   - `key`：城市中文名

   - `value`：对应的id

2. 第二种

   - `key`：城市的id
   - `value`：对应的中文名



除了上面，还需要记录省和其城市映射关系，使用 `hash` 结构保存：（前缀为 `city:info:relation`）

- `key`：省名
- `value`：其附属市级城市的集合
  - 映射关系：
    - field市级城市
    - value省级城市



### 城市id

实时数据爬取需要城市对应的id，因此需要上面拿到了市级城市然后再获取其api	

使用 Redis 缓存城市之间的id

通过爬取 https://j.i8tq.com/weather2020/search/city.js 该网页的数据进行设置

保存到 redis 的格式为：

- key：城市的中文名、拼音（前缀为`city:info:id`
- value：城市的id





### 准备爬取工作

就是爬取上面的拼音信息和城市id数据，

我们需要设置一个值，表示城市数据是否已经爬取

- 0为数据还没有进行爬取

- 2为id数据已经爬取

 `WrapRedisSpider` 用于执行前置工作，每个继承其的子类都需要在 `start_requests` 中调用其父类的 `start_prepare` 方法，开始进行准备工作：

- 首先会从redis中读取对应的状态值，是否有爬虫正在获取爬虫信息，保证更新工作仅有一个人完成
- 然后从redis读取城市数据是否已经爬取的状态，然后根据状态值来爬取不同的数据



### 实时数据爬取

以 http://www.weather.com.cn/weather1d/101300501.shtml 为例

观察网站响应，一开始返回的html并不是最终的显示效果，就说明部分数据是动态加载的

打开开发者工具中的网络，过滤出Fetch/XHR类型请求，发现并没有相关数据的请求，可以得知部分代码应该是js代码，但是是从不同的文件中返回的

过滤出js代码的请求，查看各个js文件，果然发现部分的数据是在js文件中，所需要的数据分别是

- http://d1.weather.com.cn/sk_2d/101300501.html?_=1704000321000

  ```js
  var dataSK = {
      "nameen": "guilin", // 拼音
      "cityname": "桂林",
      "city": "101300501",  // id
      "temp": "20.3", // 当前摄氏度
      "tempf": "68.5", // 当前华氏度
      "WD": "北风", // 风向
      "wde": "N", // 风向
      "WS": "3级", // 风等级
      "wse": "12km\/h", // 风速
      "SD": "50%", // 相对湿度
      "sd": "50%",
      "qy": "1000",
      "njd": "3km",
      "time": "13:10", // 该数据的时间
      "rain": "0",  // 降雨量
      "rain24h": "0", // 降雨量
      "aqi": "156", // 空气质量
      "aqi_pm25": "156", 
      "weather": "霾", // 天气描述
      "weathere": "haze",
      "weathercode": "d53",
      "limitnumber": "",
      "date": "12月31日(星期日)"
  }
  
  ```

- http://d1.weather.com.cn/dingzhi/101300501.html?_=1704000321000

  ```js
  var cityDZ101300501 = {
      "weatherinfo": {
          "city": "101300501", // 城市id
          "cityname": "桂林",
          "fctime": "202312311100", // 数据来源时间
          "temp": "21℃", // 白天温度
          "tempn": "11℃", // 黑夜温度
          "weather": "多云转小雨", // 当前天气描述
          "weathercode": "d1", 
          "weathercoden": "n7",
          "wd": "北风", // 风向
          "ws": "<3级" // 风速
      }
  };
  var alarmDZ101300501 = {
      "w": []
  }
  
  ```

除了上面的js数据，网页中还存在部分数据：

<img src="./.assets/Python%E5%A4%A7%E4%BD%9C%E4%B8%9A/image-20231231134414618.png" alt="image-20231231134414618" style="zoom:50%;" />

<img src="./.assets/Python%E5%A4%A7%E4%BD%9C%E4%B8%9A/image-20231231134427462.png" alt="image-20231231134427462" style="zoom:50%;" />

- 白天和晚上天气描述、温度、风级

- 日出日落时间

- 当前的贴心提醒

- 图表数据：最近24小时的历史温度记录、风向记录、湿度记录

  ```js
  var observe24h_data = {
                              od: {
                                  od0: "202312311200",
                                  od1: "桂林",
                                  od2: [
                                      {
                                          od21: "12", // 时间整点
                                          od22: "18.8", // 温度
                                          od23: "13", // 
                                          od24: "北风", // 风向
                                          od25: "3", // 风级
                                          od26: "0", // 降雨量
                                          od27: "54", // 湿度%
                                          od28: "", // 空气质量
                                      },
                                      {
                                          od21: "11",
                                          od22: "18.1",
                                          od23: "13",
                                          od24: "北风",
                                          od25: "2",
                                          od26: "0",
                                          od27: "58",
                                          od28: "148",
                                      },
  ```





确定爬取数据：

- 当前日期的温度值 temp (单位摄氏度)
- 当前风向 w_direction （N、W...)
- 当前风等级w_level（）
- 当前相对湿度 humidity
- 当前风速 w_speed
- 此数据的时间 timestamp
- 降雨量当前 rain
- 24小时降雨量 rain24h
- 空气质量 aqi
- 天气描述词 description



`Scrapy` 框架中的items.py中有 `RealWeatherItem` 类，结构就是爬取的数据

> Item组件就是用于存储爬取数据的结构（类似字典）



`Spider` 组件是负责获取url并解析响应体的内容

- `RealHistorySpider` 是用于获取实时天气
- 执行过程：
  - 先判断城市数据是否存在，不存在则进行爬取
  - 爬取网页数据
  - 获取http://d1.weather.com.cn/dingzhi解析
  - 获取http://d1.weather.com.cn/sk_2d/ 解析
- 之间的数据传递使用 Request的meta实现
- 最后生成 `RealItem` 传递给 pipeline

> Pipeline组件负责接收Item实例，将其保存到外部存储或者别的处理

----



### 历史天气爬取

https://tianqi.2345.com/wea_history/54511.htm

观察网络请求的发送，分析js文件，发现 `history.js` 是处理上一月和下一月数据获取的：

```js
var date = {
    'year': this.thisYear,
    'month': this.thisMonth
};
$.ajax({
    url: '/Pc/GetHistory',
    type: "get",
    data: {"areaInfo": areaInfo, date: date},
    dataType: 'json',
    success: function (res) {
        if (res.code == 1) {
            d.html(res.data);
        }
    }
});
```

当我们点击网页上的，发现多出了一个https://tianqi.2345.com/Pc/GetHistory请求

该请求为 GET 方法，参数为:

- area[type]
- area[areaId]
- date[month]
- date[year]

该请求的响应是一个json：

```js
{
  "code": 1,
  "msg": "",
  "data": "<ul class=\"history-msg\">\n  .....   </table>\n"
}
```

返回内容是指定年月的所有数据，但是是渲染到html中，所以只需要对这个进行获取并解析即可，无需解析网页



通过循环生成近五年来的所有历史数据对应的Url；

对返回的 `json` 文件使用  `lxml.html.fromstring`进行解析





### 数据传输

上面实时数据和历史数据的爬取都会产生item

这个item会被传递到 KafkaPipeline 组件，然后发送到 Kafka 的`weather-scrapy-data` 主题





## 后端

使用 Django 作为后端框架，数据库选用 mysql

![image-20240102094558481](./.assets/Python%E5%A4%A7%E4%BD%9C%E4%B8%9A/image-20240102094558481.png)

admin.py 为向管理后台注册Model信息，注册后可以在网页上直接访问数据库的所有信息以及进行增删改

app.py 为该应用 api 的配置

models.py 为该应用的数据模型，类似Springboot的数据实体+Mapper的存在

tests.py 为应用测试代码

urls.py 为 url 映射，将url映射到 views.py 的指定函数中，类似Springboot中Controller

views.py 为视图，类似Springboot中的Service，可以返回各种信息





## 前端

采用vue3+echarts+elementui编写前端页面，分别展示各种信息





## 数据分析

使用 Spark Structucted Streaming 进行数据流处理

先读取Kafka主题中的数据，根据数据中的type进行分类：实时和历史

- 实时直接保存
- 历史先保存，然后进行分析，最后保存分析数据

直接将数据保存到mysql中

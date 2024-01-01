import re
import time
import requests

header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
    "accept": "*/*",
    "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "proxy-connection": "keep-alive",
    "referer": 'http://www.weather.com.cn/',
}

if __name__ == '__main__':
    # url = 'http://d1.weather.com.cn/sk_2d/101300501.html?_=1703999982033'
    # response = requests.get(
    #     # f'http://d1.weather.com.cn/sk_2d/101300501.html?_={int(time.time() * 1000)}',
    #     url=url,
    #     headers=header,
    #
    # )
    # print(response.text)
    # import execjs
    # ctx = execjs.compile(code)
    # print(ctx.call('await send'))

    pattern = r"prov\[(\d+)] = '(.+)'"
    text = ("prov[10] = '58321-H 合肥-58321|58424-A 安庆-58424|58221-B 蚌埠-58221|58102-B 亳州-58102|58427-C 池州-58427|58236-C "
            "滁州-58236|58203-F 阜阳-58203|58116-H 淮北-58116|70931-H 黄山-70931|58224-H 淮南-58224|58311-L 六安-58311|58336-M "
            "马鞍山-58336|58122-S 宿州-58122|58429-T 铜陵-58429|58334-W 芜湖-58334|58433-X 宣城-58433'")
    a = re.match(pattern, text)
    if a:
        print(a.groups())
        content = a.group(2)
        res = re.findall(r'(\d+)-[A-Z] (\w+)-\d+', content)
        print(res)
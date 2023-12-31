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
    url = 'http://d1.weather.com.cn/sk_2d/101300501.html?_=1703999982033'
    response = requests.get(
        # f'http://d1.weather.com.cn/sk_2d/101300501.html?_={int(time.time() * 1000)}',
        url=url,
        headers=header,

    )
    print(response.text)
    # import execjs
    # ctx = execjs.compile(code)
    # print(ctx.call('await send'))
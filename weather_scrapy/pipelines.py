# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.crawler import Crawler

import logging

from utils.kafka_utils import KafkaUtils
from utils.redis_utils import RedisUtils


class WeatherScrapyPipeline:

    def process_item(self, item, spider):


        return item


class KafkaPipeline(object):
    """
    将数据发送到kafka中
    """

    @classmethod
    def from_crawler(cls, crawler: Crawler):
        # 禁止输出 item 内容
        logging.getLogger('scrapy.core.scraper').setLevel(logging.INFO)
        kafka_config = crawler.settings.get("KAFKA_CONFIG")
        redis_config = crawler.settings.get("REDIS_CONFIG")
        return cls(
            KafkaUtils(kafka_config),
            RedisUtils(redis_config)
        )

    def __init__(self, kafka: KafkaUtils, redis: RedisUtils) -> None:
        self.kafka = kafka
        self.kafka_config = kafka.config
        self.kafka.create_topics(*self.kafka_config["topics"].values())
        self.redis = redis
        self.redis_config = redis.config
        self.logger = logging.getLogger('KafkaPipeline')
        self.logger.setLevel(logging.INFO)
        self.logger.info(f'===> KafkaPipeline: kafka config {self.kafka_config}')
        self.logger.info(f'===> KafkaPipeline: redis config {self.redis_config}')

    def process_item(self, item, spider):
        """处理每个 Item """
        # 判断 Item
        if isinstance(item, RealItem):
            msgs = self.process_real_item(item, spider)
        else:
            msgs = self.process_history_item(item, spider)

        if len(msgs) > 0:
            from_currency = msgs[0]["data"]["from"]
            to_currency = msgs[0]["data"]["to"]
        else:
            from_currency = None
            to_currency = None

        if len(msgs) > 0:
            self.kafka.send_msgs(self.kafka_config['topics']['scraped'], None, *msgs)
        last_update_time = int(self.redis.get_currency_last_update_timestamp(
            from_currency,
            to_currency,
            default=time.time() * 1000
        ))
        spider.logger.info(
            f'{datetime.datetime.now()} -- {from_currency}/{to_currency}: send to kafka {len(msgs)} data, '
            f'last_update_time: {datetime.datetime.fromtimestamp(last_update_time / 1000)}'
        )
        return item

    def process_history_item(self, item, spider) -> list:
        data = item["data"]
        from_currency = data["from"]
        to_currency = data["to"]
        batchList = data["batchList"]

        # 从redis中获取最新的时间
        database_last_update_time = self.redis.get_currency_last_update_timestamp(from_currency, to_currency, -1)
        last_update_time = database_last_update_time

        result_list = []
        try:
            for x in batchList:
                start_time = x["startTime"]
                interval = x["interval"]
                rates = x["rates"]
                delta = rates[0]
                rates = rates[1:]
                for index, rate in enumerate(rates):
                    timestamp = start_time + interval * index
                    # 统计获取到的最新记录
                    if timestamp > database_last_update_time:
                        last_update_time = max(last_update_time, timestamp)
                        el = dict()
                        el["from"] = from_currency
                        el["to"] = to_currency
                        el["timestamp"] = timestamp
                        el["rate"] = rate - delta
                        result = {
                            'type': DataType.TYPE_HISTORY,
                            'data': el
                        }
                        result_list.append(result)
        except Exception as e:
            spider.logger.error(f'===> KafkaPipeline: process_history_item error: {e}')
        finally:
            self.redis.set_currency_last_update_timestamp(from_currency, to_currency, last_update_time)
            return sorted(result_list, key=lambda x: x['data']['timestamp'])

    def process_real_item(self, item, spider) -> list:
        data: list = item['data']
        result_list = []
        for d in data:
            from_currency = d["from"]
            to_currency = d["to"]
            if from_currency == to_currency:
                continue
            if not d['trend']:
                d['trend'] = "none"
            d['timestamp'] = int(datetime.datetime.now().timestamp() * 1000)
            result_list.append({
                'type': DataType.TYPE_REAL,
                'data': d
            })
        return result_list

from datetime import datetime

from scrapy.crawler import Crawler

import logging

from scrapy.exceptions import DropItem

from config import constants
from utils.kafka_utils import KafkaUtils
# from utils.kafka_utils import KafkaUtils
from weather_scrapy.items import RealWeatherItem, HistoryWeatherItem


class KafkaPipeline(object):
    """
    将数据发送到kafka中
    """

    @classmethod
    def from_crawler(cls, crawler: Crawler):
        # 禁止输出 item 内容
        logging.getLogger('scrapy.core.scraper').setLevel(logging.INFO)
        kafka_config = crawler.settings.get("KAFKA_CONFIG")
        return cls(
            KafkaUtils(kafka_config),
        )

    def __init__(self, kafka: KafkaUtils) -> None:
        self.kafka = kafka
        self.kafka_config = kafka.config
        self.kafka.create_topics(*self.kafka_config["topics"].values())
        self.logger = logging.getLogger('KafkaPipeline')
        self.logger.setLevel(logging.INFO)
        self.logger.info(f'===> KafkaPipeline: kafka config {self.kafka_config}')

    def process_item(self, item, spider):
        """处理每个 Item """
        # 判断 Item
        if isinstance(item, RealWeatherItem):
            msg = self.process_real_item(item, spider)
        elif isinstance(item, HistoryWeatherItem):
            msg = self.process_history_item(item, spider)
        else:
            msg = None
        if msg:
            self.kafka.send_msgs(self.kafka_config['topics']['scrapy'], None, msg)
            self.logger.info(
                f'======> {datetime.now()} send to kafka: {msg["data"]["city_name"]}-{msg["data"]["timestamp"]} '
            )
        raise DropItem()

    @staticmethod
    def process_history_item(item: HistoryWeatherItem, spider) -> dict | None:
        try:
            result = {
                'type': constants.DATA_TYPE_HISTORY,
                'data': dict(item)
            }
            return result
        except Exception as e:
            spider.logger.error(f'======> KafkaPipeline: process_history_item error: {e}')
            return None

    @staticmethod
    def process_real_item(item: RealWeatherItem, spider) -> dict | None:
        try:
            result = {
                'type': constants.DATA_TYPE_REAL,
                'data': dict(item)
            }
            return result
        except Exception as e:
            spider.logger.error(f'======> KafkaPipeline: process_real_item error: {e}')
            return None

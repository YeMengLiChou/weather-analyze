import logging
import time
from datetime import datetime
from multiprocessing import Process

import schedule
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def process_real():
    pro = Process(target=run_real_spider)
    pro.start()


def process_history():
    pro = Process(target=run_history_spider)
    pro.start()


def run_real_spider():
    """运行指定爬虫"""
    date = datetime.now().strftime("%Y%m%d-%H:%M")
    logger.info(f"{date}=======> start spider-real")
    crawler = CrawlerProcess(get_project_settings())
    crawler.crawl('real')
    crawler.start()


def run_history_spider():
    """运行指定爬虫"""
    date = datetime.now().strftime("%Y%m%d-%H:%M")
    logger.info(f"{date}=======> start spider-history")
    crawler = CrawlerProcess(get_project_settings())
    crawler.crawl('history')
    crawler.start()


if __name__ == '__main__':
    process_history()
    process_real()
    schedule.every(1).days.do(process_history)
    schedule.every(1).hours.do(process_real)
    while True:
        schedule.run_pending()
        time.sleep(1)
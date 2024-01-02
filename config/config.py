REDIS_CONFIG = {
    'host': '127.0.0.1',
    'port': 6379,
    'db': 0,
}

KAFKA_CONFIG = {
    'server': '127.0.0.1:9092',
    'topics': {
        'scrapy': 'weather_scrapy_topic'
    },
    'num_partitions': 1
}


MYSQL_CONFIG = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': 'anan',
    'db': 'weather',
}
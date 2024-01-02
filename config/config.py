REDIS_CONFIG = {
    'host': '127.0.0.1',
    'port': 6379,
    'db': 0,
}

KAFKA_CONFIG = {
    'bootstrap_servers': '127.0.0.1:9092',
    'topics': {
        'scrapy': 'weather_scrapy_topic'
    },
'num_partitions': 1

}
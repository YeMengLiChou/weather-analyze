import json

from kafka import KafkaProducer, KafkaConsumer, KafkaAdminClient
from kafka.admin import NewTopic
import threading
import logging
import sys
from pyspark.sql import SparkSession, DataFrame


class KafkaUtils(object):
    __ENABLE_DEBUG = True

    @classmethod
    def serializer(cls, obj):
        """
        将对象系列化为json
        :param obj:
        :return:
        """
        return json.dumps(obj, default=lambda o: o.__dict__, ensure_ascii=False).encode('utf-8')

    @classmethod
    def deserializer(cls, msg: bytes):
        return msg.decode('utf-8')

    _instance_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            with cls._instance_lock:
                if not hasattr(cls, "_instance"):
                    cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self, config) -> None:
        self.config = config
        self.__producer = self.__getKafkaProducer()
        # 设置日志为INFO,去掉无用的DEBUG信息
        logger = logging.getLogger('kafka')
        logger.addHandler(logging.StreamHandler(sys.stdout))
        logger.setLevel(logging.INFO)

        self.topics = []
        self.__admin = self.__getKafkaAdmin()
        self.__init_topics()
        pass

    def __getKafkaProducer(self) -> KafkaProducer:
        """
        获取 KafkaProducer 对象
        :return:
        """
        return KafkaProducer(
            bootstrap_servers=[self.config['server']],
            value_serializer=lambda obj: KafkaUtils.serializer(obj),
            key_serializer=lambda obj: KafkaUtils.serializer(obj),
            acks="all",
        )

    def __getKafkaAdmin(self) -> KafkaAdminClient:
        return KafkaAdminClient(
            bootstrap_servers=[self.config['server']],
        )

    def __init_topics(self):
        topics = self.__admin.list_topics()
        logging.info(f"exist topics: {topics}")
        self.topics = topics

    def create_topics(self, *topics: str):
        """
        创建新主题
        """
        need_create_topics = [
            NewTopic(
                name=topic,
                num_partitions=self.config.get("num_partitions", 2),
                replication_factor=1
            ) for topic in topics if topic not in self.topics
        ]
        if len(need_create_topics) != 0:
            self.__admin.create_topics(need_create_topics)
            self.topics.extend(need_create_topics)
            logging.info(f"create topics: {need_create_topics}")

    def send_msgs(self, topic: str, key: str | None, *data):
        """
        发送到kafka中指定的主题
        :param topic:
        :param key
        :param data:
        :return:
        """
        for d in data:
            self.__producer.send(topic, key=key, value=d)
        self.__producer.flush()

    def getKafkaConsumer(self, *topic: str) -> KafkaConsumer:
        """
        获取 KafkaConsumer 对象
        :param topic:
        :return:
        """
        return KafkaConsumer(
            *topic,
            bootstrap_servers=[self.config['server']],
            value_deserializer=lambda msg: KafkaUtils.deserializer(msg),
            # key_deserializer=lambda msg: KafkaUtils.deserializer(msg),
            auto_offset_reset="earliest",
            enable_auto_commit=True
        )

    def close(self):
        self.__producer.close()
        self.__admin.close()

    def getKafkaDataFrame(self, spark: SparkSession, offset: str | dict, *topicName: str) -> DataFrame | None:
        if offset not in ['earliest', 'latest']:
            if not isinstance(offset, dict):
                return None

        """
        获取kafka的数据流
        :param from_beginning:
        :param spark:
        :param offset: 便宜量
        :param topicName:
        :return:
        """
        return spark \
            .readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", self.config['server']) \
            .option("subscribe", ",".join(topicName)) \
            .option('startingOffsets', offset) \
            .option("failOnDataLoss", False) \
            .load() \
            .selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)", "topic", "partition", "offset", "offset",
                        "timestamp", "timestampType")

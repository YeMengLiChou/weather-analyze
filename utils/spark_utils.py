from pyspark import Row
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import *
from pyspark.sql.streaming import StreamingQuery

from ..settings import KAFKA_CONFIG


class SparkUtils:

    @staticmethod
    def get_spark_sql_session(app_name: str) -> SparkSession:
        return (
            SparkSession.builder
            .appName(app_name)
            .config('spark.jars.packages', 'org.apache.spark:spark-sql-kafka-0-10_2.13:3.5.0')
            .config('spark.sql.streaming.statefulOperator.checkCorrectness.enabled', False)
            .config("spark.streaming.kafka.maxRatePerPartition", "2000")  # 每个进程每秒最多从kafka读取的数据条数
            .config("spark.streaming.kafka.consumer.cache.enabled", False)  # 禁用UninterruptibleThread
            .master('local[*]')
            .config("failOnDataLoss", False)
            .getOrCreate()
        )

    @staticmethod
    def send_to_kafka(df: DataFrame, topic_name: str, _id: str, output_mode: str = 'append') -> StreamingQuery:
        """将数据发送到kafka指定的主题中

        :param df:
        :param topic_name:
        :param output_mode:
        :param _id
        :return:
        """
        return (
            df
            .select(to_json(struct('*')).alias('value'))
            .writeStream
            .outputMode(output_mode)  # 有新数据则发送
            .format("kafka")
            .option("kafka.bootstrap.servers", f"{KAFKA_CONFIG['server']}")
            .option("topic", f"{topic_name}")
            .option("checkpointLocation", f"tmp/check/{topic_name}/{_id}")
            .start()
        )

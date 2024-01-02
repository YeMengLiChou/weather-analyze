from pyspark.sql import DataFrame
from pyspark.sql.functions import col, from_json, udf

import config.constants
import data_store as ds
import datatype as dt
from config.config import KAFKA_CONFIG, REDIS_CONFIG
from datatype import *
from utils.kafka_utils import KafkaUtils
from utils.redis_utils import RedisUtils
from utils.spark_utils import SparkUtils

# 用于缓存数据
redis = RedisUtils(REDIS_CONFIG)

# 1天的时间间隔
day_milliseconds = 24 * 60 * 60 * 1000

# @udf
# def analyze():
#     pass


def diversion(dataframe: DataFrame):
    """
    分流数据
    :param dataframe:
    :return:
    """

    # 直接保存实时数据
    realtime_df = (
        dataframe.filter(
            col("type") == config.constants.DATA_TYPE_REAL
        )
        .select('data')
        .withColumn("json", from_json("data",  dt.real_data_schema))
        .select("json.*")
    )
    real_query = ds.save_to_mysql(realtime_df, ds.real_save, 'real')
    # 保存历史数据
    history_df: DataFrame = (
        dataframe.filter(
            col("type") == config.constants.DATA_TYPE_HISTORY
        )
        .select('data')
        .withColumn("json", from_json("data", dt.history_data_schema))
        .select("json.*")
    )
    history_query = ds.save_to_mysql(history_df, ds.real_history, 'history')

    # 分析数据
    data_df = (
        history_df
    )

    real_query.awaitTermination()
    history_query.awaitTermination()


def start_analyze():
    """
    开始分析
    :return:
    """
    spark = SparkUtils.get_spark_sql_session("rate")
    scraped_data = KAFKA_CONFIG['topics']['scrapy']

    # 读取Kafka数据
    dataframe = KafkaUtils(KAFKA_CONFIG).getKafkaDataFrame(spark, 'earliest', scraped_data)

    # 调整数据结构
    dataframe = (
        dataframe
        .select("value")  # 提取 value
        .withColumn('json', from_json(col("value"), json_schema))  # 解析 value 为 json
        .withColumn("type", col("json.type"))  # 将 json 列中的type提取出来
        .withColumn("data", col("json.data"))
        .select("type", "data")
    )

    diversion(dataframe)

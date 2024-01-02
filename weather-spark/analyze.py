from pyspark.sql import DataFrame
from pyspark.sql.functions import col, lit, udf, from_json, isnotnull
from pyspark.sql.streaming import StreamingQuery
from pyspark.sql.types import StructType, StructField, IntegerType, FloatType, Row, LongType, StringType

from config.config import KAFKA_CONFIG, REDIS_CONFIG
from utils.kafka_utils import KafkaUtils
from utils.redis_utils import RedisUtils
from utils.spark_utils import SparkUtils

# history 数据结构
history_data_schema = StructType([
    StructField('from', StringType()),
    StructField('to', StringType()),
    StructField("timestamp", LongType()),
    StructField("rate", FloatType()),
])

# kafka中的数据结构
json_schema = StructType([
    StructField("type", IntegerType()),
    StructField("data", StringType())
])

# 数据分析的结构
analyze_schema = StructType([
    StructField("time_start", LongType()),  # 起始时间
    StructField("time_end", LongType()),  # 结束时间
    StructField("max_rate", FloatType()),  # 时间段最大汇率
    StructField("min_rate", FloatType()),  # 时间段最小汇率
    StructField("average_rate", FloatType()),  # 时间段平均汇率
    StructField("start_rate", FloatType()),  # 起始汇率
    StructField("end_rate", FloatType()),  # 结束汇率
    StructField("fluctuate_change", FloatType()),  # 变化幅度（最大值-最小值）
    StructField("overall_change", FloatType()),  # 整体变化幅度（起始值-结束值）
    StructField("interval", IntegerType()),  # 时间间隔
])

# 用于缓存数据
redis = RedisUtils(REDIS_CONFIG)

# 1天的时间间隔
day_milliseconds = 24 * 60 * 60 * 1000




@udf(LongType())
def update_redis_info(from_val, to_val, timestamp, rate):
    """更新redis的信息"""
    redis.set_rate_info(from_val, to_val, rate, timestamp)
    return timestamp


@udf(analyze_schema)
def analyze(from_val, to_val, timestamp, days_interval, cur):
    """
    获取指定间隔时间的数据
    """
    ask_key_info = [(from_val, to_val, timestamp - i * day_milliseconds) for i in range(days_interval, -1, -1)]

    # 获取时间范围内的所有数据
    data = redis.get_rate_infos(ask_key_info)

    start_index = -1

    for index, d in enumerate(data):
        if d is not None:
            start_index = index
            break

    if start_index != 0:
        return None

    data = list(map(lambda x: float(x.decode()), data[start_index:]))

    # 返回结果默认值
    result = dict(
        time_start=timestamp,
        time_end=timestamp,
        max_rate=cur,
        min_rate=cur,
        average_rate=cur,
        start_rate=cur,
        end_rate=cur,
        fluctuate_change=0.0,
        overall_change=0.0,
        interval=days_interval,
    )
    result['max_rate'] = max(data)
    result['min_rate'] = min(data)
    result['average_rate'] = sum(data) / len(data)
    result['start_rate'] = data[0]
    result['end_rate'] = data[-1]
    result['fluctuate_change'] = float(result['max_rate'] - result['min_rate'])
    result['overall_change'] = float(result['start_rate'] - result['end_rate'])
    result['time_start'] = timestamp - days_interval * day_milliseconds
    result['time_end'] = timestamp
    return result


def start_analyze():
    spark = SparkUtils.get_spark_sql_session("rate")
    scraped_data = KAFKA_CONFIG['topics']['scraped']

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

    # 直接保存实时数据
    realtime_df = dataframe.filter(col("type") == DataType.TYPE_REAL).select('data')
    real_query = save_hbase(realtime_df, send_to_real)

    # 保存历史数据
    history_df = dataframe.filter(col("type") == DataType.TYPE_HISTORY).select('data')
    history_query = save_hbase(history_df, send_to_history)

    # 分析数据
    data_df = (
        history_df
        .withColumn('json', from_json(col("data"), history_data_schema))
        .select('json.*')
        .filter(col('timestamp') % day_milliseconds == 0)  # 过滤出时间为0点的数据
        .withColumn('timestamp', update_redis_info(col('from'), col('to'), col('timestamp'), col('rate')))
    )

    week_interval_query = save_hbase(
        analyze_dataframe(data_df, 7),
        send_to_analyze,
        "7"
    )
    month_interval_query = save_hbase(
        analyze_dataframe(data_df, 30),
        send_to_analyze,
        "30"
    )
    year_interval_query = save_hbase(
        analyze_dataframe(data_df, 365),
        send_to_analyze,
        "365"
    )

    real_query.awaitTermination()
    history_query.awaitTermination()
    week_interval_query.awaitTermination()
    month_interval_query.awaitTermination()
    year_interval_query.awaitTermination()


if __name__ == '__main__':
    start_analyze()
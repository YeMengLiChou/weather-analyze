from pyspark import Row
from pyspark.sql import DataFrame


def save_hbase(df: DataFrame, function, _id=None) -> StreamingQuery:
    """
    将 df 发送到 hbase 中,function 指定如何保存到hbase中
    """
    if _id:
        path = f"tmp/check/{_id}"
    else:
        path = f"tmp/check/{function.__name__}/"
    return (
        df
        .writeStream
        .outputMode('append')
        .option("checkpointLocation", path)
        .foreach(function)
        .start()
    )


def send_to_real(row: Row):
    """
    将数据保存到 hbase 的 real 表中
    """
    d = row.asDict()['data']
    ds.save_to_real(d)


def send_to_history(row: Row):
    """
    将数据保存到 hbase 的 history 中
    """
    d = row.asDict()['data']
    ds.save_to_history(d)


def send_to_analyze(row: Row):
    """
    将数据保存到 hbase 的 analyze 中
    """
    d = row.asDict()
    ds.save_to_analyze(d)


def analyze_dataframe(df: DataFrame, time_interval: int):
    """
    分析数据，设置时间间隔，计算出该时间段内的最大、最小、平均、波动值、总体变化值汇率
    """
    interval = day_milliseconds * time_interval
    return (
        df
        .select('timestamp', 'from', 'to', 'rate')
        .withColumn('interval', lit(time_interval))
        .withColumn('analyze', analyze('from', 'to', 'timestamp', 'interval', 'rate'))
        .filter(isnotnull('analyze'))  # 过滤出时间范围不满足的
        .select('from', 'to', 'analyze.*')
    )

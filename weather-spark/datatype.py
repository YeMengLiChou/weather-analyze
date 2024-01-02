from pyspark.sql.types import *

# 历史数据 数据结构
history_data_schema = StructType([
    StructField('city_name', StringType() ),
    StructField('city_id', StringType()),
    StructField("city_province", StringType()),
    StructField("timestamp", LongType()),
    StructField("description", StringType()),
    StructField("high_temp", IntegerType()),
    StructField("low_temp", IntegerType()),
    StructField("w_direction", StringType()),
    StructField("w_level", StringType()),
    StructField("aqi", IntegerType()),
    StructField("aqi_status", StringType()),
])

# kafka中的数据结构
json_schema = StructType([
    StructField("type", IntegerType()),
    StructField("data", StringType())
])

# 数据分析的结构
analyze_schema = StructType([
    StructField('')
])
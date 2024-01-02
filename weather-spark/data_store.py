import logging
import os.path

import pymysql
from pyspark import Row
from pyspark.sql import DataFrame
from pyspark.sql.streaming import StreamingQuery

from config.config import MYSQL_CONFIG

check_point = os.path.join(
    os.path.abspath(__file__).rsplit(os.sep, 2)[0],
    "checkpoint"
)

connect = pymysql.connect(**MYSQL_CONFIG)
cursor = connect.cursor()
logger = logging.getLogger('data_store')


def save_to_mysql(df: DataFrame, function, name) -> StreamingQuery:
    """
    将 df 发送到 hbase 中,function 指定如何保存到hbase中
    """
    path = os.path.join(check_point, name)
    return (
        df
        .writeStream
        .outputMode('append')
        .option("checkpointLocation", path)
        .foreach(function)
        .start()
    )


def real_save(row: Row):
    data = row.asDict()
    sql = sql_update_real(data)
    try:
        cursor.execute(sql)
        connect.commit()
    except BaseException:
        raise IOError(sql)


def real_history(row: Row):
    data = row.asDict()
    sql = sql_insert_history(data)
    try:
        cursor.execute(sql)
        connect.commit()
    except BaseException:
        raise IOError(str(data) + "\n" + sql)


def sql_update_real(real_data):
    update_real_weather = """
    INSERT INTO api_realdata 
        (city_name, city_province, city_id, temp, d_temp, n_temp, humidity, w_direction, w_level, w_speed, rain, rain24h,
         aqi, description, content, timestamp, sunrise, sunset)
    VALUES 
        ('{city_name}', '{city_province}', '{city_id}', {temp}, {d_temp}, {n_temp}, {humidity}, '{w_direction}', {w_level}, 
        {w_speed}, {rain}, {rain24h}, {aqi}, '{description}', '{content}', 
        from_unixtime({timestamp}), from_unixtime({sunrise}), from_unixtime({sunset}))
    ON DUPLICATE KEY UPDATE 
        city_name = '{city_name}', city_province = '{city_province}', temp = {temp}, d_temp = {d_temp},
        n_temp = {n_temp}, humidity = {humidity}, w_direction = '{w_direction}', w_level = {w_level}, 
        w_speed = {w_speed}, rain = {rain}, rain24h = {rain24h}, aqi = {aqi}, description = '{description}',
        content = '{content}', timestamp = from_unixtime({timestamp}),
         sunrise = from_unixtime({sunrise}), sunset = from_unixtime({sunset})
    """.format(
        city_name=real_data['city_name'],
        city_province=real_data['city_province'],
        city_id=real_data['city_id'],
        temp=real_data['temp'],
        d_temp=real_data['d_temp'],
        n_temp=real_data['n_temp'],
        humidity=real_data['humidity'],
        w_direction=real_data['w_direction'],
        w_level=real_data['w_level'],
        w_speed=real_data['w_speed'],
        rain=real_data['rain'],
        rain24h=real_data['rain24h'],
        aqi=real_data['aqi'],
        description="%s" % real_data['description'],
        content=real_data['content'],
        timestamp=real_data['timestamp'] / 1000,
        sunrise=real_data['sunrise'] / 1000,
        sunset=real_data['sunset'] / 1000,
    )
    return update_real_weather


def sql_insert_history(history_data):
    insert_history_weather = """
        INSERT
            api_historydata(city_id,city_name,city_province,timestamp,description,high_temp,low_temp,w_direction,w_level,aqi,aqi_status)
        VALUES('{city_id}','{city_name}','{city_province}',from_unixtime({timestamp}),
        '{description}',{high_temp},{low_temp},'{w_direction}',{w_level},{aqi},'{aqi_status}')
    """.format(city_id=history_data['city_id'],
               city_name=history_data['city_name'],
               city_province=history_data['city_province'],
               timestamp=history_data['timestamp'] / 1000,
               description=history_data['description'],
               high_temp=history_data['high_temp'],
               low_temp=history_data['low_temp'],
               w_direction=history_data['w_direction'],
               w_level=history_data['w_level'],
               aqi=history_data['aqi'] if history_data['aqi'] else 'NULL',
               aqi_status=history_data['aqi_status'] if history_data['aqi_status'] else '',
               )
    return insert_history_weather


if __name__ == '__main__':

    sql = sql_insert_history({
        "city_name": "香港",
        "city_id": "45007",
        "city_province": "香港",
        "timestamp": 1693324800000,
        "description": "阴~多云",
        "high_temp": 33,
        "low_temp": 27,
        "w_direction": "S",
        "w_level": 1,
        "aqi": None,
        "aqi_status": "None"
    })
    print(sql)

    res = connect.cursor().execute(sql)
    # connect.commit()
    print(res)
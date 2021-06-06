#  %SPARK_HOME%\bin\spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.0.2 extracting_streaming.py
import os
from pyspark.sql import SparkSession
from pyspark.sql import functions as f
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    IntegerType
)

JAR_FILE = os.environ["JAR_FILE"]
USER = os.environ["USER"]
PASSWORD = os.environ["PASSWORD"]
TABLE_NAME = os.environ["TABLE_NAME"]

if __name__ == "__main__":
    server = "localhost:9092"

    spark = SparkSession.builder.config("spark.jars", JAR_FILE) \
                                .master("local").appName("PySpark_MySQL") \
                                .getOrCreate()

    # spark = SparkSession.builder.appName("stream").getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")

    raw = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", server)
        .option("subscribe", "flights")
        .load()
    )

    json_schema = StructType(
        [
            StructField("Origin", StringType()),
            StructField("Destination", StringType()),
            StructField("Carrier", StringType()),
            StructField("Price", IntegerType()),
            StructField("Date", StringType()),
        ]
    )

    parsed = raw.select(
        "timestamp", f.from_json(raw.value.cast("string"), json_schema)
                      .alias("json")
    ).select(
        f.col("json").getField("Origin").alias("Origin"),
        f.col("json").getField("Destination").alias("Destination"),
        f.col("json").getField("Carrier").alias("Carrier"),
        f.col("json").getField("Price").alias("Price"),
        f.col("json").getField("Date").alias("Date"),
    )

    grouped = parsed.groupBy("Origin", "Destination", "Date")\
                    .agg(f.min(f.col("Price")).alias("Price"))

    def foreach_batch_function(df, epoch_id):
        df.write.format('jdbc') \
          .option("url", "jdbc:mysql://localhost:3306/flights") \
          .option("driver", "com.mysql.jdbc.Driver") \
          .option("dbtable", TABLE_NAME) \
          .option("user", USER).option("password", PASSWORD) \
          .mode('append').save()

    query = (parsed.writeStream
                   .outputMode("update")
                   .foreachBatch(foreach_batch_function)
                   .start())
    query.awaitTermination()
    query.stop()

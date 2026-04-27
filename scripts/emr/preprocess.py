"""
cisc886-cloud-project — Section 4
PySpark preprocessing job for Amazon Electronics Reviews
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, length, concat_ws, lit, rand
import argparse


def main(input_path, output_path):
    spark = SparkSession.builder.appName("cisc886-preprocess-beauty").getOrCreate()

    spark.sparkContext.setLogLevel("WARN")

    # ── Load ──────────────────────────────────────────────────────────────────
    print(f"[INFO] Reading from {input_path}")
    df_raw = spark.read.json(input_path)
    print(f"[INFO] Raw rows: {df_raw.count():,}")

    # ── Select columns ────────────────────────────────────────────────────────
    df = df_raw.select(
        col("asin").alias("product_id"),
        col("rating").alias("rating"),
        col("text").alias("review_text"),
        col("title").alias("review_summary"),
        col("user_id").alias("reviewer_id"),
    )

    # ── Clean ─────────────────────────────────────────────────────────────────
    df_clean = df.filter(
        col("review_text").isNotNull()
        & col("review_summary").isNotNull()
        & col("rating").isNotNull()
        & (length(col("review_text")) >= 50)
        & (length(col("review_summary")) >= 5)
        & col("rating").between(1.0, 5.0)
    )
    print(f"[INFO] After cleaning: {df_clean.count():,}")

    # ── Format as prompt/response pairs ───────────────────────────────────────
    df_final = (
        df_clean.withColumn(
            "prompt",
            concat_ws(
                " ",
                lit("A customer reviewed a beauty and personal care product with ID"),
                col("product_id"),
                lit("and gave it"),
                col("rating").cast("string"),
                lit("out of 5 stars. Review:"),
                col("review_text"),
                lit("Summarize this review."),
            ),
        )
        .withColumn("response", col("review_summary"))
        .select("product_id", "reviewer_id", "rating", "prompt", "response")
    )

    # ── Split 80 / 10 / 10 ───────────────────────────────────────────────────
    df_shuffled = df_final.orderBy(rand(seed=42))
    train, val, test = df_shuffled.randomSplit([0.8, 0.1, 0.1], seed=42)

    print(
        f"[INFO] Train: {train.count():,} | Val: {val.count():,} | Test: {test.count():,}"
    )

    # ── Write Parquet ─────────────────────────────────────────────────────────
    train.write.mode("overwrite").parquet(f"{output_path}/train/")
    val.write.mode("overwrite").parquet(f"{output_path}/val/")
    test.write.mode("overwrite").parquet(f"{output_path}/test/")

    print(f"[INFO] Written to {output_path}")
    spark.stop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    main(args.input, args.output)

import polars as pl
import os
from dotenv import load_dotenv

load_dotenv()

storage_options = {
    'account_name': 'urbancitystorages',
    'account_key': os.getenv('ACCOUNT_KEY')
}


def transform():
    source_uri = 'az://bronze/urban_service_requests.csv'
    target_uri = 'az://silver/urban_service_requests.parquet'

    df = pl.scan_csv(source_uri, storage_options=storage_options)

    column_mapping = {
        'Unique Key': 'unique_key',
        'Created Date': 'created_date',
        'Closed Date': 'closed_date',
        'Agency Name': 'agency_name',
        'Problem (formerly Complaint Type)': 'problem',
        'Problem Detail (formerly Descriptor)': 'problem_detail',
        'Additional Details': 'additional_details',
        'Location Type': 'location_type',
        'Incident Zip': 'incident_zip',
        'Incident Address': 'incident_address',
        'Street Name': 'street_name',
        'City': 'city',
        'Status': 'status',
        'Borough': 'borough',
        'Latitude': 'latitude',
        'Longitude': 'longitude'
    }

    df_refined = df.select([
        pl.col(old).alias(new) for old, new in column_mapping.items()
    ])

    # Step 1: Convert all empty strings ("") to actual nulls (None)
    # We do this first so we can accurately count them.
    df_refined = df_refined.with_columns(pl.col(pl.String).replace("", None))

    null_stats = df_refined.select([
        pl.len().alias("__total_rows"),
        *(pl.col(col).null_count().alias(col) for col in df_refined.columns)
    ]).collect()

    total_rows = null_stats["__total_rows"][0]
    threshold = total_rows * 0.90

    # 3. Keep only the columns that have fewer nulls than the threshold
    columns_to_keep = [
        col for col in df_refined.columns
        if null_stats[col][0] < threshold
    ]

    # 4. Drop the empty columns
    # 1. First, drop the empty columns
    df_refined = df_refined.select(columns_to_keep)

# 2. 🟢 FIXED: Check types using the .schema dictionary instead of subscripting
    date_columns = ["created_date", "closed_date"]
    string_cols_to_fill = [
        col for col in df_refined.columns
        if df_refined.schema[col] == pl.String and col not in date_columns
    ]

# 3. Apply "N/A" only to that safe list of columns
    df_refined = df_refined.with_columns(
        pl.col(string_cols_to_fill).fill_null("N/A")
    )

    # Split your date and time
    # We use the clean, mapped names ('created_date' and 'closed_date')
    df_refined = df_refined.with_columns(
        pl.col("created_date").str.split_exact(
            " ", 1).struct.field("field_0").alias("created_date"),
        pl.col("created_date").str.split_exact(
            " ", 1).struct.field("field_1").alias("created_time")
    )

    if "closed_date" in df_refined.columns:
        df_refined = df_refined.with_columns(
            pl.col("closed_date").str.split_exact(
                " ", 1).struct.field("field_0").alias("closed_date"),
            pl.col("closed_date").str.split_exact(
                " ", 1).struct.field("field_1").alias("closed_time")
        )

    df_refined.sink_parquet(
        target_uri,
        storage_options=storage_options,
        compression='snappy'
    )

    print(f"data loaded to {target_uri}")
    return None


# transform()

import pandas as pd
import os

def clean_data(df, logger):

    logger.info("....Starting data cleaning....")

    required_columns = [
        "InvoiceNo", "StockCode", "Description",
        "Quantity", "InvoiceDate", "UnitPrice",
        "CustomerID", "Country"
    ]

    # CHECK REQUIRED COLUMNS
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"{col} column is missing")

    logger.info("All required columns are present")

    # REMOVE DUPLICATES
    before_rows = len(df)

    df = df.drop_duplicates().copy()

    logger.info(
        f"Removed {before_rows - len(df)} duplicate rows"
    )

    # HANDLE MISSING CUSTOMER IDs
    df["CustomerID"] = (
        df["CustomerID"]
        .replace(r"^\s*$", pd.NA, regex=True)
        .fillna("Guest")
    )

    # CREATE ANOMALY FLAG
    anomaly_patterns = [
        "adjust",
        "damag",
        "missing",
        "found",
        "thrown",
        "wrong",
        "sold as",
        "dotcom",
        "amazon",
        "check",
        "broken",
        "faulty",
        "display",
        "manual",
        "wet",
        "mould",
        "crushed",
        "rusty",
        "destroy",
        "test",
        "samples",
        "discount"
    ]

    df["anomaly_flag"] = df["Description"].str.contains(
        "|".join(anomaly_patterns),
        case=False,
        na=False
    )

    logger.info(
        f"Anomaly rows flagged: {df['anomaly_flag'].sum()}"
    )

    # REMOVE INVALID INVOICE TYPES
    before_rows = len(df)

    df = df[
        ~df["InvoiceNo"]
        .astype(str)
        .str.startswith("A")
    ]

    logger.info(
        f"Removed {before_rows - len(df)} rows "
        "with InvoiceNo starting with 'A'"
    )

    # CONVERT DATE
    df["InvoiceDate"] = pd.to_datetime(
        df["InvoiceDate"],
        errors="coerce"
    )

    # STORE INVALID DATES SEPARATELY
    invalid_dates_df = df[df["InvoiceDate"].isna()].copy()

    invalid_dates_df = invalid_dates_df[
        (invalid_dates_df["Quantity"] > 0)
        &
        (invalid_dates_df["UnitPrice"] > 0)
    ]

    logger.info(
        f"Invalid date rows stored separately: "
        f"{len(invalid_dates_df)}"
    )

    # keep valid dates only
    df = df[df["InvoiceDate"].notna()].copy()

    logger.info(
        f"Rows retained after date cleaning: {len(df)}"
    )

    # TIME FEATURES
    df["year"] = df["InvoiceDate"].dt.year
    df["month"] = df["InvoiceDate"].dt.month
    df["day"] = df["InvoiceDate"].dt.day

    # TRANSACTION CLASSIFICATION
    df["transaction_type"] = "sale"

    df.loc[
        df["Quantity"] < 0,
        "transaction_type"
    ] = "return"

    df.loc[
        (df["Quantity"] > 0)
        &
        (df["UnitPrice"] == 0),
        "transaction_type"
    ] = "free_item"

    df.loc[
        df["anomaly_flag"] == True,
        "transaction_type"
    ] = "anomaly"

    # REVENUE CALCULATION
    df["revenue"] = 0.0

    sales_mask = (
        (df["Quantity"] > 0)
        &
        (df["UnitPrice"] > 0)
    )

    df.loc[
        sales_mask,
        "revenue"
    ] = (
        df["Quantity"] * df["UnitPrice"]
    )

    logger.info(
        f"Total revenue calculated: "
        f"{df['revenue'].sum():.2f}"
    )

    # EXPORT FILES
    os.makedirs("output_data", exist_ok=True)

    # CLEANED DATASET
    df.to_csv(
        "output_data/cleaned_sales_data.csv",
        index=False
    )

    df.to_excel(
        "output_data/cleaned_sales_data.xlsx",
        index=False
    )

    # ANOMALY DATASET
    anomaly_df = df[df["anomaly_flag"] == True]

    anomaly_df.to_csv(
        "output_data/anomaly_data.csv",
        index=False
    )

    anomaly_df.to_excel(
        "output_data/anomaly_data.xlsx",
        index=False
    )

    # INVALID DATE DATASET
    invalid_dates_df.to_csv(
        "output_data/invalid_date_data.csv",
        index=False
    )

    invalid_dates_df.to_excel(
        "output_data/invalid_date_data.xlsx",
        index=False
    )

    logger.info("CSV and Excel export completed")

    # CLEANING SUMMARY
    logger.info("---- Cleaning Summary ----")

    logger.info(f"Final rows: {len(df)}")

    logger.info(
        f"Sales rows: "
        f"{(df['transaction_type']=='sale').sum()}"
    )

    logger.info(
        f"Return rows: "
        f"{(df['transaction_type']=='return').sum()}"
    )

    logger.info(
        f"Free item rows: "
        f"{(df['transaction_type']=='free_item').sum()}"
    )

    logger.info(
        f"Anomaly rows: "
        f"{(df['transaction_type']=='anomaly').sum()}"
    )

    logger.info("--------------------------")

    return df, invalid_dates_df
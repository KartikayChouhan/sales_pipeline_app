import pandas as pd

def validate_data(df, logger):

    logger.info("<<......Starting data validation......>>")

    # check missing descriptions
    missing_description = df["Description"].isna().sum()

    if missing_description > 0:
        logger.warning(f"Missing descriptions found: {missing_description}")
    else:
        logger.info("No missing descriptions found")

    # check missing stock codes
    missing_stock = df["StockCode"].isna().sum()

    if missing_stock > 0:
        logger.warning(f"Missing StockCode values found: {missing_stock}")
    else:
        logger.info("No missing StockCode values found")

    # check duplicate transactions
    duplicate_sales = df.duplicated(
        subset=["InvoiceNo", "StockCode", "Quantity"],
        keep=False
    ).sum()

    logger.info(f"Potential duplicate transaction rows: {duplicate_sales}")

    # check future dates
    future_dates = df[df["InvoiceDate"] > pd.Timestamp.now()]

    if len(future_dates) > 0:
        logger.warning(f"Future dates found: {len(future_dates)}")
    else:
        logger.info("No future dates found")

    # check missing dates
    missing_dates = df["InvoiceDate"].isna().sum()

    if missing_dates > 0:
        logger.warning(f"Found {missing_dates} missing InvoiceDate values")
    else:
        logger.info("No missing InvoiceDate values found")

    # check negative revenue
    negative_revenue = (df["revenue"] < 0).sum()

    if negative_revenue > 0:
        logger.warning(f"Found {negative_revenue} rows with negative revenue")
    else:
        logger.info("No negative revenue found")

    # check invalid transaction types
    valid_types = ["sale", "return", "free_item"]

    invalid_transaction_types = (
        ~df["transaction_type"].isin(valid_types)
    ).sum()

    if invalid_transaction_types > 0:
        logger.warning(
            f"Found {invalid_transaction_types} invalid transaction types"
        )
    else:
        logger.info("All transaction types are valid")

    # check invalid sales prices
    invalid_sales = df[
        (df["transaction_type"] == "sale") &
        (df["UnitPrice"] <= 0)
    ]

    if len(invalid_sales) > 0:
        logger.warning(
            f"Found {len(invalid_sales)} sales rows with invalid UnitPrice"
        )
    else:
        logger.info("All sales rows have valid UnitPrice")

    # validate revenue calculations
    invalid_revenue = df[
        (df["transaction_type"] == "sale") &
        (df["revenue"] != df["Quantity"] * df["UnitPrice"])
    ]

    if len(invalid_revenue) > 0:
        logger.warning(
            f"Invalid revenue calculations found: {len(invalid_revenue)}"
        )
    else:
        logger.info("Revenue calculations validated successfully")

    logger.info("<<......Data validation completed......>>")
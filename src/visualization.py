import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# STYLE SETTINGS
sns.set_style("whitegrid")

# create charts folder
os.makedirs("reports/charts", exist_ok=True)

# MONTHLY REVENUE TREND
def plot_monthly_revenue(df, logger):

    sales_df = df[
        df["transaction_type"] == "sale"
    ]

    monthly_revenue = (
        sales_df
        .groupby(
            pd.Grouper(
                key="InvoiceDate",
                freq="M"
            )
        )["revenue"]
        .sum()
        .reset_index()
    )

    plt.figure(figsize=(12, 6))

    sns.lineplot(
        data=monthly_revenue,
        x="InvoiceDate",
        y="revenue",
        marker="o"
    )

    plt.title("Monthly Revenue Trend")
    plt.xlabel("Month")
    plt.ylabel("Revenue")

    plt.xticks(rotation=45)

    plt.tight_layout()

    plt.savefig(
        "reports/charts/monthly_revenue.png"
    )

    plt.close()

    logger.info("Monthly revenue chart saved")

# REVENUE BY COUNTRY
def plot_revenue_by_country(df, logger):

    sales_df = df[
        df["transaction_type"] == "sale"
    ]

    country_revenue = (
        sales_df
        .groupby("Country")["revenue"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )

    plt.figure(figsize=(12, 6))

    sns.barplot(
        x=country_revenue.values,
        y=country_revenue.index
    )

    plt.title("Top 10 Countries by Revenue")
    plt.xlabel("Revenue")
    plt.ylabel("Country")

    plt.tight_layout()

    plt.savefig(
        "reports/charts/revenue_by_country.png"
    )

    plt.close()

    logger.info("Revenue by country chart saved")

# TRANSACTION DISTRIBUTION
def plot_transaction_distribution(df, logger):

    transaction_counts = (
        df["transaction_type"]
        .value_counts()
    )

    plt.figure(figsize=(8, 8))

    plt.pie(
        transaction_counts.values,
        labels=transaction_counts.index,
        autopct="%1.1f%%"
    )

    plt.title("Transaction Type Distribution")

    plt.tight_layout()

    plt.savefig(
        "reports/charts/transaction_distribution.png"
    )

    plt.close()

    logger.info(
        "Transaction distribution chart saved"
    )

# TOP PRODUCTS
def plot_top_products(df, logger):

    sales_df = df[
        (df["transaction_type"] == "sale")
        &
        (df["Description"].notna())
    ]

    top_products = (
        sales_df
        .groupby("Description")["revenue"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )

    plt.figure(figsize=(12, 6))

    sns.barplot(
        x=top_products.values,
        y=top_products.index
    )

    plt.title("Top 10 Products by Revenue")
    plt.xlabel("Revenue")
    plt.ylabel("Product")

    plt.tight_layout()

    plt.savefig(
        "reports/charts/top_products.png"
    )

    plt.close()

    logger.info("Top products chart saved")

# MOST RETURNED PRODUCTS
def plot_most_returned_products(df, logger):

    returned_products = df[
        (df["transaction_type"] == "return")
        &
        (df["Description"].notna())
    ]

    top_returns = (
        returned_products
        .groupby("Description")["Quantity"]
        .sum()
        .abs()
        .sort_values(ascending=False)
        .head(10)
    )

    plt.figure(figsize=(12, 6))

    sns.barplot(
        x=top_returns.values,
        y=top_returns.index
    )

    plt.title("Most Returned Products")
    plt.xlabel("Returned Quantity")
    plt.ylabel("Product")

    plt.tight_layout()

    plt.savefig(
        "reports/charts/most_returned_products.png"
    )

    plt.close()

    logger.info(
        "Most returned products chart saved"
    )

# REVENUE BY TRANSACTION TYPE
def plot_revenue_by_transaction_type(df, logger):

    revenue_summary = (
        df.groupby("transaction_type")["revenue"]
        .sum()
        .sort_values(ascending=False)
    )

    plt.figure(figsize=(10, 6))

    sns.barplot(
        x=revenue_summary.index,
        y=revenue_summary.values
    )

    plt.title("Revenue by Transaction Type")
    plt.xlabel("Transaction Type")
    plt.ylabel("Revenue")

    plt.tight_layout()

    plt.savefig(
        "reports/charts/revenue_by_transaction_type.png"
    )

    plt.close()

    logger.info(
        "Revenue by transaction type chart saved"
    )

# MONTHLY RETURNS TREND
def plot_monthly_returns(df, logger):

    returns_df = df[
        df["transaction_type"] == "return"
    ]

    monthly_returns = (
        returns_df
        .groupby(
            pd.Grouper(
                key="InvoiceDate",
                freq="M"
            )
        )["Quantity"]
        .sum()
        .abs()
        .reset_index()
    )

    plt.figure(figsize=(12, 6))

    sns.lineplot(
        data=monthly_returns,
        x="InvoiceDate",
        y="Quantity",
        marker="o"
    )

    plt.title("Monthly Returns Trend")
    plt.xlabel("Month")
    plt.ylabel("Returned Quantity")

    plt.xticks(rotation=45)

    plt.tight_layout()

    plt.savefig(
        "reports/charts/monthly_returns.png"
    )

    plt.close()

    logger.info("Monthly returns chart saved")

# ANOMALY DISTRIBUTION
def plot_anomaly_distribution(df, logger):

    anomaly_counts = (
        df["anomaly_flag"]
        .value_counts()
    )

    plt.figure(figsize=(8, 6))

    sns.barplot(
        x=anomaly_counts.index.astype(str),
        y=anomaly_counts.values
    )

    plt.title("Anomaly Distribution")
    plt.xlabel("Anomaly Flag")
    plt.ylabel("Transaction Count")

    plt.tight_layout()

    plt.savefig(
        "reports/charts/anomaly_distribution.png"
    )

    plt.close()

    logger.info("Anomaly distribution chart saved")
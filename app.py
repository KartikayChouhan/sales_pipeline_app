import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")
import seaborn as sns
import io
import logging
import os

# ── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Sales Data Pipeline",
    page_icon="📊",
    layout="wide",
)

# ── CUSTOM CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Dark background */
.stApp {
    background-color: #0f1117;
    color: #e8e8e8;
}

/* Header */
.hero-title {
    font-family: 'Space Mono', monospace;
    font-size: 2.6rem;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: -1px;
    line-height: 1.1;
    margin-bottom: 0.2rem;
}
.hero-subtitle {
    font-family: 'DM Sans', sans-serif;
    font-size: 1.05rem;
    color: #8a8f9e;
    margin-bottom: 2rem;
    font-weight: 300;
}
.accent {
    color: #00e5a0;
}

/* Metric cards */
.metric-row {
    display: flex;
    gap: 1rem;
    margin: 1.5rem 0;
    flex-wrap: wrap;
}
.metric-card {
    background: #1a1d27;
    border: 1px solid #2a2d3a;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    flex: 1;
    min-width: 140px;
}
.metric-label {
    font-size: 0.75rem;
    color: #8a8f9e;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-weight: 500;
    margin-bottom: 0.4rem;
}
.metric-value {
    font-family: 'Space Mono', monospace;
    font-size: 1.7rem;
    font-weight: 700;
    color: #ffffff;
}
.metric-value.green { color: #00e5a0; }
.metric-value.red   { color: #ff6b6b; }
.metric-value.blue  { color: #60a5fa; }
.metric-value.amber { color: #fbbf24; }

/* Section headers */
.section-header {
    font-family: 'Space Mono', monospace;
    font-size: 0.8rem;
    color: #00e5a0;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin: 2.5rem 0 1rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #2a2d3a;
}

/* Upload area */
.upload-box {
    background: #1a1d27;
    border: 2px dashed #2a2d3a;
    border-radius: 16px;
    padding: 2rem;
    text-align: center;
    margin: 1rem 0;
    transition: border-color 0.2s;
}
.upload-box:hover {
    border-color: #00e5a0;
}

/* Info box */
.info-box {
    background: #1a1d27;
    border-left: 3px solid #00e5a0;
    border-radius: 0 8px 8px 0;
    padding: 1rem 1.2rem;
    margin: 1rem 0;
    font-size: 0.9rem;
    color: #8a8f9e;
}
.info-box code {
    background: #0f1117;
    color: #00e5a0;
    padding: 1px 5px;
    border-radius: 4px;
    font-family: 'Space Mono', monospace;
    font-size: 0.8rem;
}

/* Log output */
.log-box {
    background: #0a0c12;
    border: 1px solid #2a2d3a;
    border-radius: 8px;
    padding: 1rem;
    font-family: 'Space Mono', monospace;
    font-size: 0.75rem;
    color: #8a8f9e;
    max-height: 300px;
    overflow-y: auto;
    white-space: pre-wrap;
    line-height: 1.6;
}

/* Download buttons */
.stDownloadButton > button {
    background: #1a1d27 !important;
    border: 1px solid #2a2d3a !important;
    color: #e8e8e8 !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.85rem !important;
    padding: 0.5rem 1rem !important;
    transition: all 0.2s !important;
}
.stDownloadButton > button:hover {
    border-color: #00e5a0 !important;
    color: #00e5a0 !important;
}

/* Divider */
hr {
    border-color: #2a2d3a;
    margin: 2rem 0;
}

/* Hide streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ── LOGGER SETUP (in-memory for web) ──────────────────────────────────────────
def get_stream_logger():
    log_stream = io.StringIO()
    logger = logging.getLogger("pipeline_web")
    logger.setLevel(logging.INFO)
    logger.handlers = []
    handler = logging.StreamHandler(log_stream)
    handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)s | %(message)s",
                          datefmt="%H:%M:%S")
    )
    logger.addHandler(handler)
    return logger, log_stream


# ── CLEANING (copied from src/cleaning.py, no file exports) ───────────────────
def clean_data(df, logger):
    logger.info("Starting data cleaning...")

    required_columns = [
        "InvoiceNo", "StockCode", "Description",
        "Quantity", "InvoiceDate", "UnitPrice",
        "CustomerID", "Country"
    ]
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")
    logger.info("All required columns present")

    before = len(df)
    df = df.drop_duplicates().copy()
    logger.info(f"Removed {before - len(df)} duplicate rows")

    df["CustomerID"] = (
        df["CustomerID"]
        .replace(r"^\s*$", pd.NA, regex=True)
        .fillna("Guest")
    )

    anomaly_patterns = [
        "adjust","damag","missing","found","thrown","wrong",
        "sold as","dotcom","amazon","check","broken","faulty",
        "display","manual","wet","mould","crushed","rusty",
        "destroy","test","samples","discount"
    ]
    df["anomaly_flag"] = df["Description"].str.contains(
        "|".join(anomaly_patterns), case=False, na=False
    )
    logger.info(f"Anomaly rows flagged: {df['anomaly_flag'].sum()}")

    before = len(df)
    df = df[~df["InvoiceNo"].astype(str).str.startswith("A")]
    logger.info(f"Removed {before - len(df)} rows with InvoiceNo starting with 'A'")

    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce")

    invalid_dates_df = df[df["InvoiceDate"].isna()].copy()
    invalid_dates_df = invalid_dates_df[
        (invalid_dates_df["Quantity"] > 0) & (invalid_dates_df["UnitPrice"] > 0)
    ]
    logger.info(f"Invalid date rows stored separately: {len(invalid_dates_df)}")

    df = df[df["InvoiceDate"].notna()].copy()
    logger.info(f"Rows retained after date cleaning: {len(df)}")

    df["year"]  = df["InvoiceDate"].dt.year
    df["month"] = df["InvoiceDate"].dt.month
    df["day"]   = df["InvoiceDate"].dt.day

    df["transaction_type"] = "sale"
    df.loc[df["Quantity"] < 0, "transaction_type"] = "return"
    df.loc[(df["Quantity"] > 0) & (df["UnitPrice"] == 0), "transaction_type"] = "free_item"
    df.loc[df["anomaly_flag"] == True, "transaction_type"] = "anomaly"

    df["revenue"] = 0.0
    sales_mask = (df["Quantity"] > 0) & (df["UnitPrice"] > 0)
    df.loc[sales_mask, "revenue"] = df["Quantity"] * df["UnitPrice"]

    logger.info(f"Total revenue calculated: {df['revenue'].sum():.2f}")
    logger.info("Cleaning completed")

    return df, invalid_dates_df


# ── VALIDATION ─────────────────────────────────────────────────────────────────
def validate_data(df, logger):
    logger.info("Starting data validation...")

    missing_desc = df["Description"].isna().sum()
    if missing_desc > 0:
        logger.warning(f"Missing descriptions: {missing_desc}")
    else:
        logger.info("No missing descriptions")

    future_dates = df[df["InvoiceDate"] > pd.Timestamp.now()]
    if len(future_dates) > 0:
        logger.warning(f"Future dates found: {len(future_dates)}")
    else:
        logger.info("No future dates found")

    negative_revenue = (df["revenue"] < 0).sum()
    if negative_revenue > 0:
        logger.warning(f"Rows with negative revenue: {negative_revenue}")
    else:
        logger.info("No negative revenue found")

    invalid_sales = df[(df["transaction_type"] == "sale") & (df["UnitPrice"] <= 0)]
    if len(invalid_sales) > 0:
        logger.warning(f"Sales rows with invalid UnitPrice: {len(invalid_sales)}")
    else:
        logger.info("All sales rows have valid UnitPrice")

    logger.info("Validation completed")


# ── VISUALIZATIONS ─────────────────────────────────────────────────────────────
CHART_STYLE = {
    "bg":       "#1a1d27",
    "axes_bg":  "#1a1d27",
    "text":     "#8a8f9e",
    "title":    "#ffffff",
    "grid":     "#2a2d3a",
    "accent":   "#00e5a0",
    "accent2":  "#60a5fa",
    "accent3":  "#fbbf24",
    "palette":  ["#00e5a0","#60a5fa","#fbbf24","#ff6b6b","#c084fc","#fb923c"],
}

def apply_style(fig, ax):
    fig.patch.set_facecolor(CHART_STYLE["bg"])
    ax.set_facecolor(CHART_STYLE["axes_bg"])
    ax.tick_params(colors=CHART_STYLE["text"])
    ax.xaxis.label.set_color(CHART_STYLE["text"])
    ax.yaxis.label.set_color(CHART_STYLE["text"])
    ax.title.set_color(CHART_STYLE["title"])
    for spine in ax.spines.values():
        spine.set_edgecolor(CHART_STYLE["grid"])
    ax.grid(color=CHART_STYLE["grid"], linewidth=0.5)


def fig_to_image(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120, bbox_inches="tight",
                facecolor=CHART_STYLE["bg"])
    buf.seek(0)
    plt.close(fig)
    return buf


def chart_monthly_revenue(df):
    sales_df = df[df["transaction_type"] == "sale"]
    monthly = (
        sales_df.groupby(pd.Grouper(key="InvoiceDate", freq="ME"))["revenue"]
        .sum().reset_index()
    )
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(monthly["InvoiceDate"], monthly["revenue"],
            color=CHART_STYLE["accent"], marker="o", linewidth=2, markersize=4)
    ax.fill_between(monthly["InvoiceDate"], monthly["revenue"],
                    alpha=0.15, color=CHART_STYLE["accent"])
    ax.set_title("Monthly Revenue Trend", fontsize=13, pad=12)
    ax.set_xlabel("Month"); ax.set_ylabel("Revenue")
    plt.xticks(rotation=45)
    apply_style(fig, ax)
    return fig_to_image(fig)


def chart_revenue_by_country(df):
    sales_df = df[df["transaction_type"] == "sale"]
    country_rev = (
        sales_df.groupby("Country")["revenue"]
        .sum().sort_values(ascending=False).head(10)
    )
    fig, ax = plt.subplots(figsize=(10, 4))
    bars = ax.barh(country_rev.index, country_rev.values,
                   color=CHART_STYLE["accent"], alpha=0.85)
    ax.set_title("Top 10 Countries by Revenue", fontsize=13, pad=12)
    ax.set_xlabel("Revenue"); ax.set_ylabel("Country")
    ax.invert_yaxis()
    apply_style(fig, ax)
    return fig_to_image(fig)


def chart_transaction_distribution(df):
    counts = df["transaction_type"].value_counts()
    fig, ax = plt.subplots(figsize=(6, 6))
    wedges, texts, autotexts = ax.pie(
        counts.values, labels=counts.index,
        autopct="%1.1f%%",
        colors=CHART_STYLE["palette"][:len(counts)],
        textprops={"color": CHART_STYLE["text"]},
        wedgeprops={"linewidth": 2, "edgecolor": CHART_STYLE["bg"]}
    )
    for at in autotexts:
        at.set_color("#ffffff")
    ax.set_title("Transaction Type Distribution", fontsize=13, pad=12,
                 color=CHART_STYLE["title"])
    fig.patch.set_facecolor(CHART_STYLE["bg"])
    return fig_to_image(fig)


def chart_top_products(df):
    sales_df = df[(df["transaction_type"] == "sale") & df["Description"].notna()]
    top = (
        sales_df.groupby("Description")["revenue"]
        .sum().sort_values(ascending=False).head(10)
    )
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.barh(top.index, top.values, color=CHART_STYLE["accent2"], alpha=0.85)
    ax.set_title("Top 10 Products by Revenue", fontsize=13, pad=12)
    ax.set_xlabel("Revenue"); ax.set_ylabel("Product")
    ax.invert_yaxis()
    apply_style(fig, ax)
    return fig_to_image(fig)


def chart_most_returned(df):
    ret = df[(df["transaction_type"] == "return") & df["Description"].notna()]
    top = (
        ret.groupby("Description")["Quantity"]
        .sum().abs().sort_values(ascending=False).head(10)
    )
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.barh(top.index, top.values, color=CHART_STYLE["accent3"], alpha=0.85)
    ax.set_title("Most Returned Products", fontsize=13, pad=12)
    ax.set_xlabel("Returned Quantity"); ax.set_ylabel("Product")
    ax.invert_yaxis()
    apply_style(fig, ax)
    return fig_to_image(fig)


def chart_revenue_by_type(df):
    rev = df.groupby("transaction_type")["revenue"].sum().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(rev.index, rev.values,
           color=CHART_STYLE["palette"][:len(rev)], alpha=0.85)
    ax.set_title("Revenue by Transaction Type", fontsize=13, pad=12)
    ax.set_xlabel("Transaction Type"); ax.set_ylabel("Revenue")
    apply_style(fig, ax)
    return fig_to_image(fig)


def chart_monthly_returns(df):
    ret_df = df[df["transaction_type"] == "return"]
    monthly = (
        ret_df.groupby(pd.Grouper(key="InvoiceDate", freq="ME"))["Quantity"]
        .sum().abs().reset_index()
    )
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(monthly["InvoiceDate"], monthly["Quantity"],
            color=CHART_STYLE["accent3"], marker="o", linewidth=2, markersize=4)
    ax.fill_between(monthly["InvoiceDate"], monthly["Quantity"],
                    alpha=0.15, color=CHART_STYLE["accent3"])
    ax.set_title("Monthly Returns Trend", fontsize=13, pad=12)
    ax.set_xlabel("Month"); ax.set_ylabel("Returned Quantity")
    plt.xticks(rotation=45)
    apply_style(fig, ax)
    return fig_to_image(fig)


def chart_anomaly_distribution(df):
    counts = df["anomaly_flag"].value_counts()
    labels = ["Normal" if not k else "Anomaly" for k in counts.index]
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(labels, counts.values,
           color=[CHART_STYLE["accent"], CHART_STYLE["accent3"]][:len(counts)],
           alpha=0.85)
    ax.set_title("Anomaly Distribution", fontsize=13, pad=12)
    ax.set_xlabel("Flag"); ax.set_ylabel("Transaction Count")
    apply_style(fig, ax)
    return fig_to_image(fig)


# ── DOWNLOAD HELPERS ───────────────────────────────────────────────────────────
def to_csv_bytes(df):
    return df.to_csv(index=False).encode("utf-8")

def to_excel_bytes(df):
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    return buf.getvalue()

# ── SAMPLE CSV ─────────────────────────────────────────────────────────────────
SAMPLE_COLUMNS = "InvoiceNo,StockCode,Description,Quantity,InvoiceDate,UnitPrice,CustomerID,Country"
SAMPLE_ROW1    = "536365,85123A,WHITE HANGING HEART T-LIGHT HOLDER,6,2010-12-01 08:26:00,2.55,17850,United Kingdom"
SAMPLE_ROW2    = "536366,22633,HAND WARMER UNION JACK,6,2010-12-01 08:28:00,1.85,17850,United Kingdom"
SAMPLE_ROW3    = "536367,84879,ASSORTED COLOUR BIRD ORNAMENT,32,2010-12-01 08:34:00,1.69,13047,United Kingdom"
SAMPLE_ROW4    = "C536379,37446,ADJUSTMENT,1,2010-12-01 09:14:00,0.00,14527,United Kingdom"
SAMPLE_ROW5    = "536380,22960,JAM MAKING SET WITH JARS,6,2010-12-01 09:21:00,4.25,17660,Germany"
SAMPLE_CSV = "\n".join([SAMPLE_COLUMNS, SAMPLE_ROW1, SAMPLE_ROW2,
                        SAMPLE_ROW3, SAMPLE_ROW4, SAMPLE_ROW5])

# ── MAIN APP ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class='hero-title'>Sales Data <span class='accent'>Pipeline</span></div>
<div class='hero-subtitle'>Upload a retail invoice CSV — cleaning, validation, and visualization runs automatically.</div>
""", unsafe_allow_html=True)

# ── INFO BOX ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class='info-box'>
    This pipeline expects a CSV with these exact columns:<br><br>
    <code>InvoiceNo</code> &nbsp; <code>StockCode</code> &nbsp; <code>Description</code> &nbsp;
    <code>Quantity</code> &nbsp; <code>InvoiceDate</code> &nbsp; <code>UnitPrice</code> &nbsp;
    <code>CustomerID</code> &nbsp; <code>Country</code><br><br>
    Don't have a file ready? Download the sample below and upload it to see the pipeline in action.
</div>
""", unsafe_allow_html=True)

st.download_button(
    label="⬇ Download sample dataset",
    data=SAMPLE_CSV,
    file_name="sample_retail_data.csv",
    mime="text/csv",
)

st.markdown("<hr>", unsafe_allow_html=True)

# ── UPLOAD ─────────────────────────────────────────────────────────────────────
st.markdown("<div class='section-header'>Upload Your Data</div>", unsafe_allow_html=True)
uploaded_file = st.file_uploader(
    "Drop your CSV file here",
    type=["csv"],
    label_visibility="collapsed"
)

if uploaded_file is not None:

    # READ RAW DATA
    try:
        raw_df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"Could not read file: {e}")
        st.stop()

    st.markdown("<div class='section-header'>Raw Data Preview</div>",
                unsafe_allow_html=True)
    st.dataframe(raw_df.head(10), width='stretch')

    st.markdown("<hr>", unsafe_allow_html=True)

    # ROW LIMIT FOR CLOUD DEPLOYMENT
    MAX_ROWS = 50000
    if len(raw_df) > MAX_ROWS:
        st.warning(f"Your file has {len(raw_df):,} rows. This app processes up to {MAX_ROWS:,} rows on the free cloud tier. Showing results for the first {MAX_ROWS:,} rows.")
        raw_df = raw_df.head(MAX_ROWS)

    # RUN PIPELINE
    logger, log_stream = get_stream_logger()

    with st.spinner("Running pipeline..."):
        try:
            df_clean, invalid_dates_df = clean_data(raw_df.copy(), logger)
            validate_data(df_clean, logger)
        except ValueError as ve:
            st.error(str(ve))
            st.stop()
        except Exception as e:
            st.error(f"Pipeline error: {e}")
            st.stop()

    anomaly_df = df_clean[df_clean["anomaly_flag"] == True]

    # ── SUMMARY METRICS ────────────────────────────────────────────────────────
    st.markdown("<div class='section-header'>Pipeline Summary</div>",
                unsafe_allow_html=True)

    total_rows    = len(df_clean)
    total_revenue = df_clean["revenue"].sum()
    anomaly_count = len(anomaly_df)
    return_count  = (df_clean["transaction_type"] == "return").sum()
    sale_count    = (df_clean["transaction_type"] == "sale").sum()
    invalid_count = len(invalid_dates_df)

    st.markdown(f"""
    <div class='metric-row'>
        <div class='metric-card'>
            <div class='metric-label'>Clean Rows</div>
            <div class='metric-value blue'>{total_rows:,}</div>
        </div>
        <div class='metric-card'>
            <div class='metric-label'>Total Revenue</div>
            <div class='metric-value green'>£{total_revenue:,.0f}</div>
        </div>
        <div class='metric-card'>
            <div class='metric-label'>Sales</div>
            <div class='metric-value'>{sale_count:,}</div>
        </div>
        <div class='metric-card'>
            <div class='metric-label'>Returns</div>
            <div class='metric-value amber'>{return_count:,}</div>
        </div>
        <div class='metric-card'>
            <div class='metric-label'>Anomalies</div>
            <div class='metric-value red'>{anomaly_count:,}</div>
        </div>
        <div class='metric-card'>
            <div class='metric-label'>Invalid Dates</div>
            <div class='metric-value'>{invalid_count:,}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── CHARTS ─────────────────────────────────────────────────────────────────
    st.markdown("<div class='section-header'>Visualizations</div>",
                unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.image(chart_monthly_revenue(df_clean), width='stretch')
    with col2:
        st.image(chart_revenue_by_country(df_clean), width='stretch')

    col3, col4 = st.columns(2)
    with col3:
        st.image(chart_top_products(df_clean), width='stretch')
    with col4:
        st.image(chart_most_returned(df_clean), width='stretch')

    col5, col6 = st.columns(2)
    with col5:
        st.image(chart_monthly_returns(df_clean), width='stretch')
    with col6:
        st.image(chart_revenue_by_type(df_clean), width='stretch')

    col7, col8 = st.columns(2)
    with col7:
        st.image(chart_transaction_distribution(df_clean), width='stretch')
    with col8:
        st.image(chart_anomaly_distribution(df_clean), width='stretch')

    # ── DOWNLOADS ──────────────────────────────────────────────────────────────
    st.markdown("<div class='section-header'>Download Outputs</div>",
                unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.markdown("**Cleaned Data**")
        st.download_button("⬇ CSV",   to_csv_bytes(df_clean),
                           "cleaned_data.csv",   "text/csv",        key="clean_csv")
        st.download_button("⬇ Excel", to_excel_bytes(df_clean),
                           "cleaned_data.xlsx",
                           "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                           key="clean_xlsx")

    with col_b:
        st.markdown("**Anomaly Data**")
        st.download_button("⬇ CSV",   to_csv_bytes(anomaly_df),
                           "anomaly_data.csv",   "text/csv",        key="anom_csv")
        st.download_button("⬇ Excel", to_excel_bytes(anomaly_df),
                           "anomaly_data.xlsx",
                           "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                           key="anom_xlsx")

    with col_c:
        st.markdown("**Invalid Date Rows**")
        st.download_button("⬇ CSV",   to_csv_bytes(invalid_dates_df),
                           "invalid_dates.csv",  "text/csv",        key="inv_csv")
        st.download_button("⬇ Excel", to_excel_bytes(invalid_dates_df),
                           "invalid_dates.xlsx",
                           "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                           key="inv_xlsx")

    # ── PIPELINE LOG ───────────────────────────────────────────────────────────
    st.markdown("<div class='section-header'>Pipeline Log</div>",
                unsafe_allow_html=True)
    log_output = log_stream.getvalue()
    st.markdown(f"<div class='log-box'>{log_output}</div>", unsafe_allow_html=True)

else:
    st.markdown("""
    <div style='text-align:center; padding: 3rem 0; color: #2a2d3a;'>
        <div style='font-size: 3rem;'>📂</div>
        <div style='font-family: Space Mono, monospace; font-size: 0.85rem;
                    color: #3a3d4a; margin-top: 1rem; letter-spacing: 1px;'>
            WAITING FOR FILE UPLOAD
        </div>
    </div>
    """, unsafe_allow_html=True)

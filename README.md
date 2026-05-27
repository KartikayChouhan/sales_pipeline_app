# Sales Data Pipeline

An end-to-end data cleaning and visualization pipeline for retail invoice data, deployed as an interactive web application.

**Live App → [salespipelineap-gn3tw96y66z5pg48p6dygl.streamlit.app](https://salespipelineap-gn3tw96y66z5pg48p6dygl.streamlit.app/)**

---

## What It Does

Upload a raw retail invoice CSV and the pipeline automatically:

- Cleans the data — removes duplicates, handles missing customer IDs, filters invalid invoice types, and parses dates
- Detects anomalies — flags rows containing keywords like damaged, broken, faulty, missing, and 20+ other patterns
- Classifies transactions — categorizes every row as a sale, return, free item, or anomaly
- Calculates revenue — computes revenue for all valid sales transactions
- Validates the output — checks for future dates, negative revenue, invalid prices, and missing values
- Generates 8 visualizations — monthly revenue trend, top countries, top products, most returned products, monthly returns, revenue by transaction type, transaction distribution, and anomaly distribution
- Exports results — cleaned data, anomaly data, and invalid date rows available as CSV and Excel downloads

---

## Dataset Format

This pipeline is designed for retail invoice data with the following columns:

| Column | Description |
|--------|-------------|
| `InvoiceNo` | Invoice number (rows starting with 'A' are filtered out) |
| `StockCode` | Product stock code |
| `Description` | Product description (used for anomaly detection) |
| `Quantity` | Units purchased (negative = return) |
| `InvoiceDate` | Date and time of transaction |
| `UnitPrice` | Price per unit |
| `CustomerID` | Customer identifier (missing values filled as 'Guest') |
| `Country` | Customer country |

Don't have a dataset? The app includes a **Download Sample Dataset** button to test the pipeline instantly.

---

## Tech Stack

- **Python** — core pipeline logic
- **Pandas** — data cleaning and transformation
- **Matplotlib / Seaborn** — visualizations
- **Streamlit** — web application framework
- **OpenPyXL** — Excel file export

---

## Project Structure

```
sales_pipeline_app/
├── src/
│   ├── cleaning.py        # Cleaning rules and anomaly flagging
│   ├── validation.py      # Post-cleaning data validation
│   ├── visualization.py   # Chart generation functions
│   ├── ingestion.py       # File loading utilities
│   └── logger.py          # Pipeline logging setup
├── app.py                 # Streamlit web application
└── requirements.txt       # Python dependencies
```

---

## Run Locally

```bash
# Clone the repo
git clone https://github.com/KartikayChouhan/sales_pipeline_app.git
cd sales_pipeline_app

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

---

## Pipeline Logic

**Anomaly Detection**
Rows are flagged as anomalies if their description contains any of 22 keywords including: adjust, damaged, missing, broken, faulty, wrong, test, discount, and others. These rows are separated into their own export file rather than deleted, preserving the data for review.

**Transaction Classification**
Every row is classified into one of four types:
- `sale` — positive quantity and positive price
- `return` — negative quantity
- `free_item` — positive quantity with zero price
- `anomaly` — flagged by the anomaly detection rules

**Invalid Date Handling**
Rows with unparseable dates are not deleted. If they have valid quantity and price values, they are stored separately in an invalid dates export file.

---



# 🛒 Olist Customer Experience Intelligence Platform

> An end-to-end customer analytics platform combining NLP, sentiment analysis, machine learning, and business intelligence to transform raw e-commerce data into actionable insights.

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)](https://postgresql.org)
[![Power BI](https://img.shields.io/badge/Power%20BI-Dashboard-yellow)](https://powerbi.microsoft.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-Live%20App-red)](https://olist-customer-intelligence-5b2dopipfmaatguqumxrjz.streamlit.app)

---

## 🔗 Live Demo

**Streamlit App:** [Customer Feedback Portal](https://olist-customer-intelligence-5b2dopipfmaatguqumxrjz.streamlit.app)

> Staff login credentials available upon request for dashboard access demonstration.

---

## 📋 Project Overview

This project builds a complete customer experience intelligence system for **Olist**, Brazil's largest e-commerce marketplace, analyzing **96,000+ orders**, **93,000+ customers**, and **11,578 customer reviews** across two market regions.

The platform automatically:
- Collects and classifies customer feedback by theme and sentiment
- Routes complaints to relevant departments in real time
- Alerts management when negative review spikes are detected
- Provides secure, role-based staff access to review data
- Forecasts revenue trends using machine learning

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    DATA SOURCES                         │
│         Olist E-commerce Dataset (Kaggle)               │
└──────────────────────┬──────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────┐
│                  DATA LAYER                             │
│         PostgreSQL — 9 tables, 15 SQL views             │
│    Window Functions │ CTEs │ RFM Analysis               │
└──────────────────────┬──────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────┐
│                ANALYTICS LAYER                          │
│   NLP Pipeline │ Sentiment Analysis │ ML Clustering     │
│   VADER │ KMeans │ Linear Regression Forecast           │
└──────────────────────┬──────────────────────────────────┘
                       ↓
┌───────────────────────────────────────┐  ┌─────────────┐
│         STREAMLIT APPLICATION         │  │  POWER BI   │
│  Customer Form │ Staff Dashboard      │  │  5-Page     │
│  Google Sheets │ Role-based Auth      │  │  Dashboard  │
└──────────────────────┬────────────────┘  └─────────────┘
                       ↓
┌─────────────────────────────────────────────────────────┐
│               AUTOMATION LAYER                          │
│   Weekly Email Reports │ Real-time Spike Alerts         │
│   3-tier Alert System │ Department Routing              │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Key Features

### 1. 🗄️ SQL Database (PostgreSQL)
- 9 normalized tables from Olist dataset
- 15 analytical views including:
  - Regional KPIs and revenue analysis
  - Delivery performance metrics
  - Customer segmentation (RFM Analysis)
  - Month-over-month growth (LAG window function)
  - Product revenue ranking (RANK window function)

### 2. 🧠 NLP & Sentiment Analysis Pipeline
- Translated 9,839 Portuguese reviews to English using `deep_translator`
- Keyword-based theme classification across **12 themes** (99.7% coverage)
- VADER sentiment analysis: Positive 60.96% / Neutral 23.78% / Negative 15.26%
- Sentiment alignment validation: **65.94%** match between text and star ratings
- KMeans customer segmentation (Low / Medium / High Value)

### 3. 🌐 Streamlit Web Application
- **Customer tab:** Public feedback form with duplicate detection and email validation
- **Staff tab:** Secure login with username/password authenticated against Google Sheets
- Role-based access — each department sees only their relevant reviews
- Auto theme classification + sentiment scoring on submission
- Real-time data persistence via Google Sheets API

### 4. 📧 Automated Email Alert System
- **Weekly reports:** Every Monday 8:00 AM — department-specific summaries
- **Spike alerts:** Every 6 hours — 3-tier system:
  - 🟡 WARNING: 3+ negative reviews same theme in 24hrs
  - 🟠 HIGH: 5+ negative reviews same theme in 24hrs
  - 🔴 CRITICAL: 10+ negative reviews same theme in 24hrs
- Secure workflow — emails contain dashboard link, not raw customer data
- Department routing: Logistics / Warehouse / Finance / Customer Support / Supplier Relations

### 5. 📊 Power BI Dashboard (5 Pages)
| Page | Focus | Key Insight |
|------|-------|-------------|
| Market Overview | Revenue & Operations |$15.42M revenue, Region B declining -26% MoM |
| Customer Intelligence | Segments & Retention | Only 2.98% repeat rate — retention crisis |
| Sentiment Analysis | NLP Insights | Delivery & Shipping dominates complaints |
| Strategic Intelligence | Themes & Delivery | Wrong Item has most negative sentiment |
| Recommendations | Forecast & Actions | Revenue forecast Sep-Nov 2018 (R²=0.84) |

### 6. 🤖 Machine Learning — Revenue Forecast
- Linear Regression model trained on 24 months of historical data
- **R² = 0.8426** — model explains 84% of revenue variance
- **RMSE = R$83,590**
- Predictions for Sep-Nov 2018:
  - Region A: R$746K → R$773K → R$799K
  - Region B: R$567K → R$593K → R$620K

---

## 📁 Repository Structure

```
olist-customer-intelligence/
│
├── scripts/                         # Python scripts
│   ├── app.py                       # Streamlit web application
│   ├── email_alerts.py              # Automated email alert system
│   └── revenue_forecast.py         # ML revenue forecast model
│
├── notebook/                       # Jupyter notebooks
│   ├── 01_sentiment_analysis.ipynb  # NLP pipeline & VADER analysis
│   ├── 02_customer_segmentation.ipynb # KMeans clustering
│   └── 03_data_validation.ipynb    # Data quality validation
│
├── sql/                             # PostgreSQL queries
│   ├── 01_create_tables.sql        # Table definitions
│   ├── 02_views_core.sql           # 12 core analytical views
│   └── 03_views_advanced.sql       # Window functions, CTEs, RFM
│
├── dashboard/                       # Power BI screenshots
│   ├── Market Overview.jpeg
│   ├── Customer Intelligence.jpeg
│   ├── Sentiment Analysis.png
│   ├── Strategic Intelligence.jpeg
│   └── Recommendations & Predictions.jpeg
│
├── requirements.txt                 # Python dependencies
└── README.md                        # Project documentation
```

---

## 🛠️ Tech Stack

| Category | Technology |
|----------|-----------|
| Database | PostgreSQL 15 |
| Language | Python 3.11 |
| NLP | VADER Sentiment, deep_translator |
| ML | scikit-learn (KMeans, Linear Regression) |
| Web App | Streamlit |
| Data Storage | Google Sheets API |
| BI Dashboard | Microsoft Power BI |
| Automation | Python schedule, smtplib |
| Version Control | Git / GitHub |

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Google Cloud account (for Sheets API)

### 1. Clone the repository
```bash
git clone https://github.com/maeenmohammed2027/olist-customer-intelligence.git
cd olist-customer-intelligence
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Download the dataset
Download the Olist Brazilian E-Commerce dataset from Kaggle:
[https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)

Place all CSV files in a `data/` folder.

### 4. Set up PostgreSQL
```bash
psql -U postgres -f sql/01_create_tables.sql
psql -U postgres -f sql/02_views_core.sql
psql -U postgres -f sql/03_views_advanced.sql
```

### 5. Configure Google Sheets credentials
- Create a Google Cloud project
- Enable Google Sheets API and Google Drive API
- Create a service account and download `credentials.json`
- Place `credentials.json` in the root folder

### 6. Run the Streamlit app
```bash
streamlit run scripts/app.py
```

### 7. Run email alerts
```bash
python scripts/email_alerts.py
```

---

## 📊 Dashboard Screenshots

### Page 1 — Market Overview
![Market Overview](dashboard/Market%20Overview.jpeg)

### Page 2 — Customer Intelligence
![Customer Intelligence](dashboard/Customer%20Intelligence.jpeg)

### Page 3 — Sentiment Analysis
![Sentiment Analysis](dashboard/Sentiment%20Analysis.png)

### Page 4 — Strategic Intelligence
![Strategic Intelligence](dashboard/Strategic%20Intelligence.jpeg)

### Page 5 — Recommendations & Predictions
![Recommendations](dashboard/Recommendations%20%26%20Predictions.jpeg)

---

## 📈 Key Business Findings

1. **Delivery Crisis in Region B** — Late delivery rate 8.89% vs 5.47% in Region A. Average delivery takes 16.4 days vs 10.5 days. Region B revenue declining -26% MoM.

2. **Retention Emergency** — Only 2.98% of customers make a repeat purchase. High Value customers spend **8x more** than Low Value customers (R$1,031 vs R$132).

3. **Delivery Dominates Complaints** — 5,710 of 11,578 reviews (49.3%) relate to Delivery & Shipping — the single largest complaint theme.

4. **Wrong Item = Most Negative** — Wrong Item Received has the most negative average sentiment score (-0.13), indicating high customer frustration.

5. **Revenue Growing** — From R$143 in September 2016 to R$985K in August 2018 — a **6,870x increase** over 24 months.

---

## 🔐 Security Features

- Staff dashboard protected by username/password authentication
- Credentials stored securely in Google Sheets (not hardcoded)
- Role-based access — each department sees only their data
- Email alerts contain secure app link — no raw customer data in emails
- `credentials.json` excluded from repository via `.gitignore`

---

## 📝 Data Notes

- **Missing values:** 83 rows missing product/order details, 148 rows missing product category
- **Sentiment alignment:** 65.94% match between VADER text sentiment and star ratings — 34.06% of customers rate differently than they write
- **Region definition:** Region A = SP, RJ, MG states (core market). Region B = all other states (expansion market)

---

## 👤 Author

**Maeen Mohammed**
Senior Data & Business Intelligence Analyst
14+ years experience in data, BI, and MERL roles

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue)](https://linkedin.com/in/maeenmohammed)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-black)](https://github.com/maeenmohammed2027)

---

## 📄 License

This project uses the [Olist Brazilian E-Commerce Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) available on Kaggle under CC BY-NC-SA 4.0 license.

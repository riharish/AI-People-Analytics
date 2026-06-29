# Text-to-SQL: People Analytics & Intelligence

A natural language analytics tool for people data. Ask any workforce question in plain English — get an instant answer, a dynamic chart, and the SQL query behind it.

No dashboards to navigate. No filters to set. Just ask.

---

## Demo

> "Which department has the highest attrition rate?"

> "Do employees who work overtime leave more?"

> "How does salary vary across job levels?"

> "Which job role is paid the most?"

The app generates a SQL query, runs it against the dataset, interprets the result, and returns a concise insight with a chart — all in seconds.

---

## How it works

```
User types a question
        ↓
LLM reads the table schema and writes a SQL query
        ↓
SQLite executes the query on the dataset
        ↓
LLM interprets the result and generates an insight + chart instructions
        ↓
Plotly renders the chart dynamically
```

The LLM never sees raw employee rows — only the table schema and aggregated query results. Fast, token-efficient, and easy to swap for any tabular HR dataset.

---

## Tech stack

| Layer | Tool |
|---|---|
| UI | Streamlit |
| LLM | Groq API — llama-3.1-8b-instant |
| Query execution | SQLite (in-memory) |
| Data processing | Pandas |
| Visualization | Plotly |
| Environment | Python-dotenv |

---

## Setup

**1. Clone the repo**
```bash
git clone https://github.com/yourusername/people-analytics.git
cd people-analytics
```

**2. Download the dataset**

This project uses the IBM HR Analytics Attrition dataset from Kaggle.

https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset

Save the downloaded file as:
```
data/hr_data.csv
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Set up your Groq API key**

Create a `.env` file in the project root:
```
GROQ_API_KEY=your_key_here
```

Get a free key at https://console.groq.com — no credit card required.

**5. Run**
```bash
streamlit run app.py
```

---

## Project structure

```
people_analytics/
│
├── data/
│   └── hr_data.csv          ← IBM HR dataset (download separately)
│
├── app.py                   ← Streamlit UI and orchestration
├── data_loader.py           ← CSV loading, AttritionFlag derivation, SQLite setup
├── groq_engine.py           ← SQL generation and answer interpretation via Groq
├── chart_builder.py         ← Dynamic Plotly chart rendering
│
├── .env                     ← API key (never committed)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Dataset

IBM HR Analytics Attrition Dataset — 1,470 employees, 35 variables covering demographics, compensation, tenure, satisfaction scores, and attrition status. Widely used benchmark dataset for people analytics work.

---

## Extending this project

- **Swap the dataset** — replace `hr_data.csv` with any HR export. Update `get_schema()` in `data_loader.py` if needed.
- **Swap the LLM** — replace Groq with OpenAI, Azure OpenAI, or any OpenAI-compatible API by updating the client in `groq_engine.py`.
- **Add authentication** — wrap with Streamlit's built-in auth or deploy behind SSO for internal use.
- **Connect to a live database** — replace the SQLite in-memory setup with a live Postgres or Snowflake connection for real-time workforce data.


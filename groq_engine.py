import os
import json
import pandas as pd
import sqlite3
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def generate_sql(question: str, schema: str) -> str:
    """
    Call 1 — Groq reads schema + question, writes SQL query.
    Returns SQL string.
    """

    prompt = f"""
You are an expert SQL analyst. Given a table schema and a question, write a SQL query to answer it.

{schema}

QUESTION:
{question}

COLUMN GUIDANCE:
- Salary/income/compensation = MonthlyIncome only
- DailyRate, MonthlyRate, HourlyRate are NOT salary — never use these for salary questions
- Attrition rate = AVG(AttritionFlag) * 100 AS AttritionRate
- Tenure/years at company = YearsAtCompany
- "Longest serving" or "average tenure" = AVG(YearsAtCompany)
- "Oldest employee" or "most years" for an individual = MAX(YearsAtCompany)
- Job satisfaction = JobSatisfaction (scale 1-4)
- Work life balance = WorkLifeBalance (scale 1-4)
- Environment satisfaction = EnvironmentSatisfaction (scale 1-4)
- Relationship satisfaction = RelationshipSatisfaction (scale 1-4)
- When asked about pay/salary for a role or group, use AVG(MonthlyIncome) not MAX or MIN unless explicitly asked for highest/lowest individual salary

RULES:
- Write a single valid SQLite SQL query
- Query the table called "employees"
- Return ONLY the SQL query, nothing else
- No markdown, no explanation, no backticks
- Select ONLY the columns directly needed to answer the question, never add extra columns
- Always use AVG(AttritionFlag) * 100 AS AttritionRate for attrition rate calculations
- Always alias calculated columns with clear names e.g. AS AttritionRate, AS AvgSalary, AS EmployeeCount
- Always put the grouping column first, calculated columns second
- When comparing groups always use GROUP BY to return ALL groups, never filter with WHERE to a single group
- Never use LIMIT unless the question explicitly asks for top N or bottom N
- Never use aggregate functions in WHERE clause, use HAVING instead
- If the question asks for highest or lowest, return ALL groups ordered by the metric DESC so the chart shows full comparison
- When asked about pay/salary for a role or group, use AVG(MonthlyIncome)
- Always use ORDER BY [metric] DESC unless question specifically asks for lowest first
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": "You are a SQL expert. Return only a valid SQLite SQL query. No markdown, no explanation, no backticks. Only SELECT columns directly needed to answer the question. Never add extra columns."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.1,
        max_tokens=300
    )

    sql = response.choices[0].message.content.strip()

    if sql.startswith("```"):
        sql = sql.split("```")[1]
        if sql.lower().startswith("sql"):
            sql = sql[3:]
        sql = sql.strip()

    return sql


def execute_sql(sql: str, conn: sqlite3.Connection) -> tuple:
    """
    Executes SQL on in-memory SQLite db.
    Returns (result_df, error_message).
    """
    try:
        result_df = pd.read_sql_query(sql, conn)
        return result_df, None
    except Exception as e:
        return None, str(e)


def generate_answer(question: str, sql: str, result: pd.DataFrame, schema: str) -> dict:
    """
    Call 2 — Groq reads question + SQL + result, returns answer + chart JSON.
    """

    prompt = f"""
You are a people analytics assistant at BCG (Boston Consulting Group).
You help HR partners and leadership answer workforce questions instantly.

TABLE SCHEMA:
{schema}

USER QUESTION:
{question}

SQL QUERY EXECUTED:
{sql}

QUERY RESULT:
{result.to_string(index=False)}

INSTRUCTIONS:
- Read the FULL query result carefully before forming your answer
- The first row in the result is always the highest value when ordered DESC — lead with that
- Never skip rows from the result when summarizing
- Use specific numbers from the result only, never approximate
- Always format currency values with $ prefix and 2 decimal places e.g. $6,686.57
- Always round all numbers to 2 decimal places in the answer text
- Never use backticks anywhere in the answer text
- Be concise and insight-forward, like a BCG analyst briefing a partner
- 2-3 sentences maximum

RESPOND ONLY WITH THIS JSON:
{{
    "answer": "2-3 sentence insight, lead with the actual highest/lowest finding from first row, use specific numbers",
    "chart_type": "bar" or "histogram" or "box" or "scatter" or "pie" or "none",
    "chart_column": "column name from result to plot on x axis, or null",
    "chart_value": "column name from result to plot on y axis, or null",
    "chart_group": "column name to color by, or null",
    "chart_title": "short chart title, or null",
    "insight_tag": "one of: attrition, compensation, tenure, satisfaction, headcount, diversity, workload"
}}

CHART RULES:
- bar: comparing categories (Department, JobRole, JobLevel)
- histogram: distribution of a numeric column (Age, MonthlyIncome)
- box: spread across groups (MonthlyIncome by JobLevel)
- scatter: relationship between two numeric columns
- pie: simple part-to-whole (Gender split, Attrition split)
- none: purely factual, chart adds nothing
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": "You are a people analytics AI. Always respond with valid JSON only. No markdown, no preamble."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2,
        max_tokens=500
    )

    raw = response.choices[0].message.content.strip()

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.lower().startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        result_json = json.loads(raw)
        # fix backtick formatting Groq keeps adding
        if "answer" in result_json:
            result_json["answer"] = result_json["answer"].replace("`", "$")
    except json.JSONDecodeError:
        result_json = {
            "answer": "I had trouble interpreting the result. Please try rephrasing.",
            "chart_type": "none",
            "chart_column": None,
            "chart_value": None,
            "chart_group": None,
            "chart_title": None,
            "insight_tag": "headcount"
        }

    return result_json
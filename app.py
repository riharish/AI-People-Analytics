import streamlit as st
from data_loader import load_data, load_db, get_schema
from groq_engine import generate_sql, execute_sql, generate_answer
from chart_builder import build_chart

# page config
st.set_page_config(
    page_title="People Analytics | BCG",
    page_icon="📊",
    layout="wide"
)

# load data once at startup
@st.cache_resource
def init():
    df = load_data()
    conn = load_db(df)
    schema = get_schema(df)
    return df, conn, schema

df, conn, schema = init()

# header
st.title("People Analytics")
st.caption("Ask any question about the workforce data in plain English.")

st.divider()

# KPI row — computed from actual data, no hardcoding
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Employees", f"{len(df):,}")

with col2:
    if "AttritionFlag" in df.columns:
        rate = round(df["AttritionFlag"].mean() * 100, 1)
        st.metric("Attrition Rate", f"{rate}%")

with col3:
    if "YearsAtCompany" in df.columns:
        tenure = round(df["YearsAtCompany"].mean(), 1)
        st.metric("Avg Tenure", f"{tenure} yrs")

with col4:
    if "MonthlyIncome" in df.columns:
        salary = round(df["MonthlyIncome"].mean(), 0)
        st.metric("Avg Monthly Income", f"${salary:,.0f}")

st.divider()

# chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if "chart" in msg and msg["chart"] is not None:
            st.plotly_chart(msg["chart"], use_container_width=True)
        if "sql" in msg and msg["sql"]:
            with st.expander("View SQL query"):
                st.code(msg["sql"], language="sql")

# chat input
question = st.chat_input("Ask anything — e.g. which department has highest attrition?")

if question:
    # display user message
    with st.chat_message("user"):
        st.write(question)
    st.session_state.messages.append({"role": "user", "content": question})

    # generate response
    with st.chat_message("assistant"):
        with st.spinner("Analyzing..."):

            # step 1 — generate SQL
            sql = generate_sql(question, schema)

            # step 2 — execute SQL
            result_df, error = execute_sql(sql, conn)

            if error:
                st.error(f"Could not run query: {error}")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"Could not run query: {error}",
                    "chart": None,
                    "sql": sql
                })

            else:
                # step 3 — generate answer + chart instructions
                answer_json = generate_answer(question, sql, result_df, schema)

                answer_text = answer_json.get("answer", "No answer generated.")
                st.write(answer_text)

                # step 4 — build chart if needed
                chart = build_chart(answer_json, result_df)
                if chart:
                    st.plotly_chart(chart, use_container_width=True)

                # show SQL in expander
                with st.expander("View SQL query"):
                    st.code(sql, language="sql")

                # save to history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer_text,
                    "chart": chart,
                    "sql": sql
                })
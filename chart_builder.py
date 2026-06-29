import plotly.express as px
import pandas as pd


def build_chart(chart_json: dict, result_df: pd.DataFrame):
    """
    Takes Groq's chart instructions + SQL result dataframe.
    Returns a Plotly figure or None if no chart needed.
    """

    chart_type = chart_json.get("chart_type", "none")

    if chart_type == "none" or not chart_type:
        return None

    chart_column = chart_json.get("chart_column")
    chart_value = chart_json.get("chart_value")
    chart_group = chart_json.get("chart_group")
    chart_title = chart_json.get("chart_title", "")

    # validate columns exist in result_df
    if chart_column and chart_column not in result_df.columns:
        return None
    if chart_value and chart_value not in result_df.columns:
        return None
    if chart_group and chart_group not in result_df.columns:
        chart_group = None

    try:
        if chart_type == "bar":
            fig = px.bar(
                result_df,
                x=chart_column,
                y=chart_value,
                color=chart_group,
                title=chart_title
            )

        elif chart_type == "histogram":
            fig = px.histogram(
                result_df,
                x=chart_column,
                color=chart_group,
                title=chart_title
            )

        elif chart_type == "box":
            fig = px.box(
                result_df,
                x=chart_column,
                y=chart_value,
                color=chart_group,
                title=chart_title
            )

        elif chart_type == "scatter":
            fig = px.scatter(
                result_df,
                x=chart_column,
                y=chart_value,
                color=chart_group,
                title=chart_title
            )

        elif chart_type == "pie":
            fig = px.pie(
                result_df,
                names=chart_column,
                values=chart_value,
                title=chart_title
            )

        else:
            return None

        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(size=13),
            margin=dict(t=40, b=40, l=20, r=20)
        )

        return fig

    except Exception:
        return None
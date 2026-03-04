import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="ShopSmart Sales Dashboard", layout="wide")


REQUIRED_COLUMNS = {
    "date", "order_id", "product", "category",
    "region", "quantity", "unit_price", "total_amount",
}


@st.cache_data
def load_data(filepath: str = "data/sales-data.csv") -> pd.DataFrame:
    try:
        df = pd.read_csv(filepath)
    except FileNotFoundError:
        st.error(f"Data file not found: '{filepath}'. Ensure data/sales-data.csv is present at the repo root.")
        st.stop()
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Unexpected error loading data: {e}")
        st.stop()
        return pd.DataFrame()

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        st.error(f"Data file is missing required columns: {sorted(missing)}")
        st.stop()
        return pd.DataFrame()

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    invalid_dates = int(df["date"].isna().sum())
    if invalid_dates > 0:
        st.warning(f"{invalid_dates} row(s) with invalid dates excluded from charts.")
        df = df.dropna(subset=["date"])

    return df


def calculate_kpis(df: pd.DataFrame) -> dict:
    return {
        "total_sales": float(df["total_amount"].sum()),
        "total_orders": len(df),
    }


def prepare_trend_data(df: pd.DataFrame) -> pd.DataFrame:
    date_range = df["date"].max() - df["date"].min()
    freq = "D" if date_range.days <= 30 else "MS"
    trend = (
        df.groupby(pd.Grouper(key="date", freq=freq))["total_amount"]
        .sum()
        .reset_index()
        .rename(columns={"date": "month", "total_amount": "sales"})
    )
    return trend.sort_values("month").reset_index(drop=True)


def prepare_category_data(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("category")["total_amount"]
        .sum()
        .reset_index()
        .rename(columns={"total_amount": "sales"})
        .sort_values("sales", ascending=False)
        .reset_index(drop=True)
    )


def prepare_region_data(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("region")["total_amount"]
        .sum()
        .reset_index()
        .rename(columns={"total_amount": "sales"})
        .sort_values("sales", ascending=False)
        .reset_index(drop=True)
    )


def build_trend_chart(trend_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure(
        go.Scatter(
            x=trend_df["month"],
            y=trend_df["sales"],
            mode="lines+markers",
            line=dict(color="#F47A20"),
            marker=dict(color="#F47A20"),
            hovertemplate="%{x|%b %Y}<br>$%{y:,.2f}<extra></extra>",
        )
    )
    fig.update_layout(
        title="Sales Trend Over Time",
        xaxis_title="Month",
        yaxis_title="Total Sales ($)",
    )
    return fig


def build_category_chart(cat_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure(
        go.Bar(
            x=cat_df["category"],
            y=cat_df["sales"],
            marker_color="#1E4FAF",
            hovertemplate="%{x}<br>$%{y:,.2f}<extra></extra>",
        )
    )
    fig.update_layout(
        title="Sales by Category",
        xaxis_title="Category",
        yaxis_title="Total Sales ($)",
    )
    return fig


def build_region_chart(region_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure(
        go.Bar(
            x=region_df["region"],
            y=region_df["sales"],
            marker_color="#1E4FAF",
            hovertemplate="%{x}<br>$%{y:,.2f}<extra></extra>",
        )
    )
    fig.update_layout(
        title="Sales by Region",
        xaxis_title="Region",
        yaxis_title="Total Sales ($)",
    )
    return fig


def main() -> None:
    st.title("ShopSmart Sales Dashboard")

    try:
        df = load_data()
    except Exception as e:
        st.error(f"Unexpected error loading data: {e}")
        st.stop()
        return

    kpis = calculate_kpis(df)
    col1, col2 = st.columns(2)
    col1.metric("Total Sales", f"${kpis['total_sales']:,.2f}")
    col2.metric("Total Orders", f"{kpis['total_orders']:,}")

    trend_df = prepare_trend_data(df)
    st.plotly_chart(build_trend_chart(trend_df), use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        cat_df = prepare_category_data(df)
        st.plotly_chart(build_category_chart(cat_df), use_container_width=True)
    with col2:
        region_df = prepare_region_data(df)
        st.plotly_chart(build_region_chart(region_df), use_container_width=True)


if __name__ == "__main__":
    main()

import pandas as pd
import pytest
from unittest.mock import patch
from dashboard import (
    load_data,
    calculate_kpis,
    prepare_trend_data,
    prepare_category_data,
    prepare_region_data,
)


@pytest.fixture(autouse=True)
def clear_streamlit_cache():
    """Clear st.cache_data before each test to prevent cross-test pollution."""
    import streamlit as st
    st.cache_data.clear()
    yield


def test_placeholder():
    pass


# --- load_data ---

def test_load_data_returns_correct_shape():
    df = load_data("data/sales-data.csv")
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 482
    assert df.shape[1] == 8


def test_load_data_has_required_columns():
    df = load_data("data/sales-data.csv")
    expected = {
        "date", "order_id", "product", "category",
        "region", "quantity", "unit_price", "total_amount",
    }
    assert expected.issubset(set(df.columns))


def test_load_data_date_column_is_datetime():
    df = load_data("data/sales-data.csv")
    assert pd.api.types.is_datetime64_any_dtype(df["date"])


def test_load_data_file_not_found_handled_gracefully():
    with patch("streamlit.error") as mock_error, patch("streamlit.stop") as mock_stop:
        load_data("nonexistent_file_xyz.csv")
        mock_error.assert_called_once()
        mock_stop.assert_called_once()


# --- calculate_kpis ---

def test_calculate_kpis_returns_required_keys():
    df = pd.DataFrame({"total_amount": [10.0, 20.0, 30.0]})
    result = calculate_kpis(df)
    assert "total_sales" in result
    assert "total_orders" in result


def test_calculate_kpis_total_orders_is_row_count():
    df = pd.DataFrame({"total_amount": [10.0, 20.0, 30.0]})
    result = calculate_kpis(df)
    assert result["total_orders"] == 3


def test_calculate_kpis_total_sales_is_sum():
    df = pd.DataFrame({"total_amount": [10.0, 20.0, 30.0]})
    result = calculate_kpis(df)
    assert result["total_sales"] == pytest.approx(60.0)


# --- prepare_trend_data ---

def _make_trend_df(dates, amounts):
    return pd.DataFrame({
        "date": pd.to_datetime(dates),
        "total_amount": amounts,
    })


def test_prepare_trend_data_output_columns():
    df = _make_trend_df(["2024-01-15", "2024-02-15", "2024-03-15"], [100.0, 200.0, 300.0])
    result = prepare_trend_data(df)
    assert "month" in result.columns
    assert "sales" in result.columns


def test_prepare_trend_data_sorted_ascending():
    df = _make_trend_df(["2024-03-15", "2024-01-15", "2024-02-15"], [300.0, 100.0, 200.0])
    result = prepare_trend_data(df)
    assert result["month"].is_monotonic_increasing


def test_prepare_trend_data_monthly_aggregation_for_long_range():
    # Two transactions in Jan, one in Feb — range > 30 days → monthly freq
    df = _make_trend_df(["2024-01-10", "2024-01-20", "2024-02-10"], [100.0, 50.0, 200.0])
    result = prepare_trend_data(df)
    assert len(result) == 2
    assert result["sales"].iloc[0] == pytest.approx(150.0)  # Jan
    assert result["sales"].iloc[1] == pytest.approx(200.0)  # Feb


def test_prepare_trend_data_daily_aggregation_for_short_range():
    # Range is 9 days (≤30) → daily freq, one row per distinct date
    df = _make_trend_df(["2024-01-01", "2024-01-05", "2024-01-10"], [100.0, 200.0, 300.0])
    result = prepare_trend_data(df)
    assert len(result) >= 3


# --- prepare_category_data ---

def _make_category_df(categories, amounts):
    return pd.DataFrame({
        "category": categories,
        "total_amount": amounts,
    })


def test_prepare_category_data_output_columns():
    df = _make_category_df(["A", "B", "C"], [100.0, 200.0, 300.0])
    result = prepare_category_data(df)
    assert "category" in result.columns
    assert "sales" in result.columns


def test_prepare_category_data_sorted_descending():
    df = _make_category_df(["A", "B", "C"], [100.0, 300.0, 200.0])
    result = prepare_category_data(df)
    assert result["sales"].is_monotonic_decreasing


def test_prepare_category_data_all_categories_present():
    df = _make_category_df(["A", "B", "C", "A"], [100.0, 200.0, 300.0, 50.0])
    result = prepare_category_data(df)
    assert set(result["category"]) == {"A", "B", "C"}


def test_prepare_category_data_sales_is_sum_per_category():
    df = _make_category_df(["A", "B", "A"], [100.0, 200.0, 50.0])
    result = prepare_category_data(df)
    a_sales = result.loc[result["category"] == "A", "sales"].iloc[0]
    b_sales = result.loc[result["category"] == "B", "sales"].iloc[0]
    assert a_sales == pytest.approx(150.0)
    assert b_sales == pytest.approx(200.0)

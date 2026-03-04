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

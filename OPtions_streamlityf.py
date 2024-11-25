import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Alpha Vantage API Key
API_KEY = "4GPS846F30484987"

# Set up the page layout
st.set_page_config(page_title="Stock Option Analysis", layout="wide")

# Sidebar for user inputs
st.sidebar.title("Options Analysis Settings")
ticker = st.sidebar.text_input("Enter stock ticker (e.g., TSLA):", value="TSLA")
include_expired = st.sidebar.checkbox("Include expired options", value=False)
selected_date = None

# Title
st.title("Stock Option Analysis")
st.markdown("Analyze stock options, visualize trends, and track specific option performance.")

if ticker:
    # Fetch stock metadata
    try:
        stock_url = f"https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={ticker}&apikey={API_KEY}"
        stock_data = requests.get(stock_url).json()

        if "bestMatches" in stock_data and stock_data["bestMatches"]:
            st.success(f"Found stock: {stock_data['bestMatches'][0]['2. name']} ({ticker.upper()})")
        else:
            st.error("Stock not found. Please check the ticker.")
    except Exception as e:
        st.error(f"Error fetching stock data: {e}")

    # Placeholder for option expiration dates (Alpha Vantage lacks options directly)
    st.sidebar.subheader("Available Option Expiration Dates")
    option_dates = ["2024-12-15", "2025-01-19"]  # Placeholder for demo
    selected_date = st.sidebar.selectbox("Choose an expiration date:", option_dates)

    if selected_date:
        st.subheader(f"Options Data for {ticker} - Expiration Date: {selected_date}")
        # Fetch time series data
        try:
            time_series_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={ticker}&apikey={API_KEY}"
            time_series_data = requests.get(time_series_url).json()

            if "Time Series (Daily)" in time_series_data:
                df = pd.DataFrame.from_dict(time_series_data["Time Series (Daily)"], orient="index", dtype=float)
                df = df.reset_index().rename(columns={
                    "index": "Date",
                    "1. open": "Open",
                    "2. high": "High",
                    "3. low": "Low",
                    "4. close": "Close",
                    "6. volume": "Volume"
                })
                df["Date"] = pd.to_datetime(df["Date"])
                df.sort_values("Date", inplace=True)

                # Plot price trend
                st.markdown("#### Price Trend")
                price_fig = px.line(
                    df,
                    x="Date",
                    y=["Open", "Close", "High", "Low"],
                    title=f"Price Trend for {ticker}",
                    labels={"value": "Price", "variable": "Metric", "Date": "Date"},
                )
                st.plotly_chart(price_fig, use_container_width=True)

                # Plot volume trend
                st.markdown("#### Volume Trend")
                volume_fig = px.bar(
                    df,
                    x="Date",
                    y="Volume",
                    title=f"Volume Trend for {ticker}",
                    labels={"Volume": "Volume", "Date": "Date"},
                )
                st.plotly_chart(volume_fig, use_container_width=True)

                # Combined price and volume overlay plot
                st.markdown("#### Combined Price and Volume Trend")
                overlay_fig = go.Figure()

                # Add price trends
                overlay_fig.add_trace(go.Scatter(
                    x=df["Date"],
                    y=df["Close"],
                    mode="lines",
                    name="Close Price",
                    line=dict(color="blue", width=2),
                ))

                # Add volume bars
                overlay_fig.add_trace(go.Bar(
                    x=df["Date"],
                    y=df["Volume"],
                    name="Volume",
                    marker=dict(color="rgba(255, 182, 193, 0.6)"),
                    yaxis="y2",
                ))

                # Configure layout for dual y-axes
                overlay_fig.update_layout(
                    title=f"Price and Volume Trend for {ticker}",
                    xaxis_title="Date",
                    yaxis=dict(title="Price", titlefont=dict(color="blue"), tickfont=dict(color="blue")),
                    yaxis2=dict(
                        title="Volume",
                        titlefont=dict(color="red"),
                        tickfont=dict(color="red"),
                        anchor="x",
                        overlaying="y",
                        side="right",
                    ),
                    legend=dict(x=0.1, y=1.1, orientation="h"),
                    margin=dict(l=40, r=40, t=50, b=40),
                )
                st.plotly_chart(overlay_fig, use_container_width=True)
            else:
                st.error("No time series data available.")
        except Exception as e:
            st.error(f"Error fetching time series data: {e}")

# Footer
st.markdown("---")
st.markdown("Created using [Streamlit](https://streamlit.io/) and [Alpha Vantage API](https://www.alphavantage.co/).")

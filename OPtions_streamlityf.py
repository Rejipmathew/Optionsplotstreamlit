import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

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
    # Fetch stock data
    stock = yf.Ticker(ticker)
    option_dates = stock.options

    if option_dates:
        st.sidebar.subheader("Available Option Expiration Dates")
        selected_date = st.sidebar.selectbox("Choose an expiration date:", option_dates)
        if include_expired:
            st.sidebar.warning("Expired options will be fetched, which might take longer.")
    else:
        st.error("No option data available for this stock.")

    if selected_date:
        st.subheader(f"Options Data for {ticker} - Expiration Date: {selected_date}")
        # Fetch option chain for the selected date
        try:
            option_chain = stock.option_chain(selected_date)
            calls = option_chain.calls
            puts = option_chain.puts

            # Combine calls and puts for specific option analysis
            all_options = pd.concat([calls, puts]).reset_index(drop=True)
            st.sidebar.subheader("Analyze Specific Option")
            option_symbol = st.sidebar.selectbox("Select an option contract:", all_options["contractSymbol"].unique())

            # Display plots for the selected option
            if option_symbol:
                st.subheader(f"Trend Analysis for {option_symbol}")

                # Fetch historical data for the selected option
                try:
                    historical_data = yf.download(option_symbol, period="1mo", interval="1d")
                    if not historical_data.empty:
                        historical_data.reset_index(inplace=True)
                        
                        # Plot price trend
                        st.markdown("#### Price Trend")
                        price_fig = px.line(
                            historical_data,
                            x="Date",
                            y=["Open", "Close", "High", "Low"],
                            title=f"Price Trend for {option_symbol}",
                            labels={"value": "Price", "variable": "Metric", "Date": "Date"},
                        )
                        st.plotly_chart(price_fig, use_container_width=True)

                        # Plot volume trend
                        st.markdown("#### Volume Trend")
                        volume_fig = px.bar(
                            historical_data,
                            x="Date",
                            y="Volume",
                            title=f"Volume Trend for {option_symbol}",
                            labels={"Volume": "Volume", "Date": "Date"},
                        )
                        st.plotly_chart(volume_fig, use_container_width=True)
                    else:
                        st.error("No historical data available for this option.")
                except Exception as e:
                    st.error(f"Error fetching historical data: {e}")

            # Show sorted data by volume
            st.markdown("### Calls Data Sorted by Volume")
            calls_sorted = calls.sort_values(by="volume", ascending=False)
            st.dataframe(calls_sorted)

            st.markdown("### Puts Data Sorted by Volume")
            puts_sorted = puts.sort_values(by="volume", ascending=False)
            st.dataframe(puts_sorted)
        except Exception as e:
            st.error(f"Error fetching option chain data: {e}")

# Footer
st.markdown("---")
st.markdown("Created using [Streamlit](https://streamlit.io/) and [Yahoo Finance API](https://pypi.org/project/yfinance/).")

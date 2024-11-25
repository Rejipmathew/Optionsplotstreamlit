import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# Set up the page layout
st.set_page_config(page_title="Stock Option Analysis", layout="wide")

# Sidebar for user inputs
st.sidebar.title("Options Analysis Settings")
ticker = st.sidebar.text_input("Enter stock ticker (e.g., TSLA):", value="TSLA")
include_expired = st.sidebar.checkbox("Include expired options", value=False)

# Title
st.title("Stock Option Analysis")
st.markdown("Analyze stock options, visualize trends, and track specific option performance.")

if ticker:
    # Fetch stock data
    stock = yf.Ticker(ticker)
    option_dates = stock.options

    if option_dates:
        st.sidebar.subheader("Available Option Expiration Dates")
        # Default to the first expiration date if none is selected
        selected_date = st.sidebar.selectbox("Choose an expiration date:", option_dates, index=0)
        if include_expired:
            st.sidebar.warning("Expired options will be fetched, which might take longer.")
    else:
        st.error("No option data available for this stock.")

    if selected_date:
        st.subheader(f"Options Data for {ticker} - Expiration Date: {selected_date}")
        try:
            # Fetch option chain for the selected date
            option_chain = stock.option_chain(selected_date)
            calls = option_chain.calls
            puts = option_chain.puts

            # Combine calls and puts for specific option analysis
            all_options = pd.concat([calls, puts]).reset_index(drop=True)
            st.sidebar.subheader("Analyze Specific Option")
            option_symbol = st.sidebar.selectbox("Select an option contract:", all_options["contractSymbol"].unique())

            if option_symbol:
                st.subheader(f"Trend Analysis for {option_symbol}")

                # Fetch historical data for the selected option
                try:
                    historical_data = yf.download(option_symbol, period="1mo", interval="1d")
                    if not historical_data.empty:
                        historical_data.reset_index(inplace=True)

                        # Convert columns to scalar values if necessary
                        for col in ["Open", "High", "Low", "Close", "Volume"]:
                            historical_data[col] = historical_data[col].apply(
                                lambda x: x[0] if isinstance(x, (list, pd.Series, pd.DataFrame)) else x
                            )

                        # Price Trend Plot
                        st.markdown("#### Price Trend")
                        fig, ax = plt.subplots(figsize=(10, 6))
                        ax.plot(historical_data["Date"], historical_data["Open"], label="Open", color="blue")
                        ax.plot(historical_data["Date"], historical_data["High"], label="High", color="green")
                        ax.plot(historical_data["Date"], historical_data["Low"], label="Low", color="red")
                        ax.plot(historical_data["Date"], historical_data["Close"], label="Close", color="black")
                        ax.set_title(f"Price Trend for {option_symbol}")
                        ax.set_xlabel("Date")
                        ax.set_ylabel("Price")
                        ax.legend()
                        st.pyplot(fig)

                        # Volume Trend Plot
                        st.markdown("#### Volume Trend")
                        fig, ax = plt.subplots(figsize=(10, 6))
                        ax.bar(historical_data["Date"], historical_data["Volume"], color="purple")
                        ax.set_title(f"Volume Trend for {option_symbol}")
                        ax.set_xlabel("Date")
                        ax.set_ylabel("Volume")
                        st.pyplot(fig)

                        # Combined Price and Volume Plot
                        st.markdown("#### Combined Price and Volume Trend")
                        fig, ax1 = plt.subplots(figsize=(10, 6))
                        ax1.plot(historical_data["Date"], historical_data["Close"], label="Close Price", color="blue")
                        ax1.set_xlabel("Date")
                        ax1.set_ylabel("Price", color="blue")
                        ax1.tick_params(axis="y", labelcolor="blue")

                        ax2 = ax1.twinx()
                        ax2.bar(historical_data["Date"], historical_data["Volume"], color="gray", alpha=0.5, label="Volume")
                        ax2.set_ylabel("Volume", color="gray")
                        ax2.tick_params(axis="y", labelcolor="gray")

                        fig.suptitle(f"Price and Volume Trend for {option_symbol}")
                        fig.tight_layout()
                        st.pyplot(fig)
                    else:
                        st.error("No historical data available for this option.")
                except Exception as e:
                    st.error(f"Error fetching historical data: {e}")

            # Display sorted data by volume
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

import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime

# FMP API key
api_key = '416c95d58e894f9806fe1318cc4a4cbf'

# Function to get tickers, company names, sector, and industry
def get_sp500_data():
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    tables = pd.read_html(url)
    sp500_table = tables[0]
    sp500_table['Symbol'] = sp500_table['Symbol'].replace({'BRK.B': 'BRK-B', 'BF.B': 'BF-B'})
    sp500_data = sp500_table[['Symbol', 'Security', 'GICS Sector', 'GICS Sub-Industry']]
    sp500_data.columns = ['Ticker Symbol', 'Company Name', 'Sector', 'Industry']
    return sp500_data

# Function to get adjusted closing prices
def download_adjusted_close_prices(start_date='2024-01-01'):
    sp500_data = get_sp500_data()
    tickers = sp500_data['Ticker Symbol'].tolist()
    end_date = datetime.now().strftime('%Y-%m-%d')
    all_data = {}
    failed_tickers = []

    for ticker in tickers:
        print(f"Downloading data for {ticker}...")
        try:
            data = yf.download(ticker, start=start_date, end=end_date, progress=False)
            if not data.empty:
                all_data[ticker] = data['Adj Close']
            else:
                failed_tickers.append(ticker)
        except Exception as e:
            failed_tickers.append(ticker)
            print(f"Failed to download data for {ticker}: {e}")
    
    if failed_tickers:
        print(f"Failed to download data for the following tickers: {', '.join(failed_tickers)}")
        
    all_data_df = pd.DataFrame(all_data)
    return all_data_df, sp500_data

# function to calculate top ten price returns
def top_ten(start_date, end_date):

    # Filter all_data_df for the specified date range
    filtered_data = all_data_df.loc[start_date:end_date]

    # Ensure we have data for the exact start and end dates
    if start_date not in filtered_data.index or end_date not in filtered_data.index:
        raise ValueError("Data for the specified start or end date is not available in the filtered data.")

    # Calculate the percentage price change for each ticker
    start_prices = filtered_data.loc[start_date]
    end_prices = filtered_data.loc[end_date]
    price_change = round(((end_prices - start_prices) / start_prices) * 100,2)

    # Sort the tickers by price change in descending order
    top_ten_tickers = price_change.sort_values(ascending=False).head(10)

    # Merge the top ten tickers with the sp500_data to get company details
    top_ten_details = pd.merge(
        top_ten_tickers.reset_index(),
        sp500_data,
        left_on='index',
        right_on='Ticker Symbol'
    )

    # Drop the redundant 'Ticker Symbol' column
    top_ten_details.drop(columns=['Ticker Symbol'], inplace=True)
    # Rename columns for clarity
    top_ten_details.rename(columns={0: 'Price Return (%)', 'index': 'Ticker Symbol'}, inplace=True)
    top_ten_details = top_ten_details[['Ticker Symbol', 'Company Name', 'Sector', 'Industry', 'Price Return (%)']]

    # Sort the details by price return for clarity
    top_ten_details = top_ten_details.sort_values(by='Price Return (%)', ascending=False)
    # return top_ten_details
    return top_ten_details

# function to calculate bottom ten price returns
def bottom_ten(start_date, end_date):

    # Filter all_data_df for the specified date range
    filtered_data = all_data_df.loc[start_date:end_date]

    # Ensure we have data for the exact start and end dates
    if start_date not in filtered_data.index or end_date not in filtered_data.index:
        raise ValueError("Data for the specified start or end date is not available in the filtered data.")

    # Calculate the percentage price change for each ticker
    start_prices = filtered_data.loc[start_date]
    end_prices = filtered_data.loc[end_date]
    price_change = round(((end_prices - start_prices) / start_prices) * 100,2)

    # Sort the tickers by price change in descending order
    bottom_ten_tickers = price_change.sort_values(ascending=True).head(10)

    # Merge the top ten tickers with the sp500_data to get company details
    bottom_ten_details = pd.merge(
        bottom_ten_tickers.reset_index(),
        sp500_data,
        left_on='index',
        right_on='Ticker Symbol'
    )

    # Drop the redundant 'Ticker Symbol' column
    bottom_ten_details.drop(columns=['Ticker Symbol'], inplace=True)
    # Rename columns for clarity
    bottom_ten_details.rename(columns={0: 'Price Return (%)', 'index': 'Ticker Symbol'}, inplace=True)
    bottom_ten_details = bottom_ten_details[['Ticker Symbol', 'Company Name', 'Sector', 'Industry', 'Price Return (%)']]

    # Sort the details by price return for clarity
    bottom_ten_details = bottom_ten_details.sort_values(by='Price Return (%)', ascending=False)
    # return top_ten_details
    return bottom_ten_details

# Main function to run the Streamlit app
def main():
    st.title("S&P 500 Top and Bottom Performers")

    # Sidebar for user input
    st.sidebar.header("User Input")
    start_date = st.sidebar.date_input("Start Date", datetime(2024, 8, 8))
    end_date = st.sidebar.date_input("End Date", datetime(2024, 8, 9))

    if start_date > end_date:
        st.error("Error: End Date must fall after Start Date.")
    else:
        # Download data (consider caching this for performance)
        global all_data_df, sp500_data
        all_data_df, sp500_data = download_adjusted_close_prices()

        # Calculate top ten and bottom ten
        top_ten_df = top_ten(str(start_date), str(end_date))
        bottom_ten_df = bottom_ten(str(start_date), str(end_date))

        # Display results
        st.subheader(f"Top 10 Performers from {start_date} to {end_date}")
        st.dataframe(top_ten_df)

        st.subheader(f"Bottom 10 Performers from {start_date} to {end_date}")
        st.dataframe(bottom_ten_df)

if __name__ == '__main__':
    main()

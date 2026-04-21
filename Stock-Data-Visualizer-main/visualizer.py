import requests
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
import numpy as np
import time

def createGraph(StartTime, EndTime, DesiredGraph, Company, TimeSeries):
    # Map time series to Alpha Vantage API functions
    API_KEY = "H0XQD306IFOZECWX"
    function_map = {
        '1': 'TIME_SERIES_INTRADAY',
        '2': 'TIME_SERIES_DAILY',
        '3': 'TIME_SERIES_WEEKLY',
        '4': 'TIME_SERIES_MONTHLY'
    }
    
    # Map time series to output key in JSON response
    output_key_map = {
        '1': 'Time Series (5min)',
        '2': 'Time Series (Daily)',
        '3': 'Weekly Time Series',
        '4': 'Monthly Time Series'
    }
    
    
    # Prepare API request parameters
    base_url = 'https://www.alphavantage.co/query'
    params = {
        'function': function_map[TimeSeries.lower()],
        'symbol': Company.upper(),
        'apikey': API_KEY,
        'outputsize': 'full'  # Get full historical data
    }
    
    # Add interval parameter for intraday data
    if TimeSeries.lower() == 'intraday':
        params['interval'] = '5min'  # Can be 1min, 5min, 15min, 30min, 60min
        params['adjusted'] = 'true'
        params['extended_hours'] = 'true'
        output_key_map['intraday'] = f'Time Series ({params["interval"]})'
    
    # Make API request
    try:
        print(f"Fetching {TimeSeries} data for {Company}...")
        response = requests.get(base_url, params=params)
        data = response.json()
        
        # Check for API errors
        if 'Error Message' in data:
            raise ValueError(f"API Error: {data['Error Message']}")
        if 'Note' in data:
            print(f"API Note: {data['Note']}")
            print("Waiting 60 seconds before retry...")
            time.sleep(60)
            response = requests.get(base_url, params=params)
            data = response.json()
        
        # Extract time series data
        time_series_key = output_key_map[TimeSeries.lower()]
        if time_series_key not in data:
            raise ValueError(f"No {TimeSeries} data found for {Company}")
        
        time_series_data = data[time_series_key]
        
        # Convert to DataFrame
        df = pd.DataFrame.from_dict(time_series_data, orient='index')
        df.index = pd.to_datetime(df.index)
        df.sort_index(inplace=True)
        
        # Convert price columns to float
        price_cols = [col for col in df.columns if 'open' in col.lower() or 
                     'high' in col.lower() or 'low' in col.lower() or 
                     'close' in col.lower()]
        for col in price_cols:
            df[col] = pd.to_numeric(df[col])
        
        # Filter by date range
        start_date = pd.to_datetime(StartTime)
        end_date = pd.to_datetime(EndTime)
        df = df[(df.index >= start_date) & (df.index <= end_date)]
        
        if df.empty:
            raise ValueError(f"No data found for {Company} in the specified date range")
        
        print(f"Successfully retrieved {len(df)} data points")
        
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None
    
    # Create the figure and axis
    fig, ax = plt.subplots(figsize=(14, 7))
    
    # Use closing price for the graph
    close_col = '4. close' if '4. close' in df.columns else '4. close'
    if close_col not in df.columns:
        # Try alternative column names
        for col in df.columns:
            if 'close' in col.lower():
                close_col = col
                break
    
    # Plot based on desired graph type
    if DesiredGraph.lower() == 'line':
        ax.plot(df.index, df[close_col], 
                color='blue', linewidth=2, label=f'{Company} Close Price')
        ax.fill_between(df.index, df[close_col], 
                        alpha=0.3, color='blue')
        
    elif DesiredGraph.lower() == 'bar':
        # Color bars based on price movement
        colors = []
        for i in range(len(df)):
            if i == 0:
                colors.append('green')
            else:
                if df[close_col].iloc[i] >= df[close_col].iloc[i-1]:
                    colors.append('green')
                else:
                    colors.append('red')
        
        ax.bar(df.index, df[close_col], 
               color=colors, alpha=0.7, width=0.8)
        
    else:
        raise ValueError(f"Invalid DesiredGraph. Choose from: 'bar' or 'line'")
    
    # Customize the graph
    ax.set_title(f'{Company} Stock Price - {TimeSeries.title()} Data\n{StartTime} to {EndTime}', 
                 fontsize=14, fontweight='bold')
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Price (USD)', fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45)
    
    # Add statistics
    current_price = df[close_col].iloc[-1]
    start_price = df[close_col].iloc[0]
    price_change = current_price - start_price
    price_change_pct = (price_change / start_price) * 100
    
    # Find max and min prices
    max_price = df[close_col].max()
    min_price = df[close_col].min()
    max_date = df[close_col].idxmax()
    min_date = df[close_col].idxmin()
    
    # Add text box with stats
    stats_text = f'Current: ${current_price:.2f}\n'
    stats_text += f'Change: ${price_change:.2f} ({price_change_pct:.2f}%)\n'
    stats_text += f'Max: ${max_price:.2f} ({max_date.strftime("%Y-%m-%d")})\n'
    stats_text += f'Min: ${min_price:.2f} ({min_date.strftime("%Y-%m-%d")})'
    
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
            fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout()
    
    # Show the plot
    #plt.show()
    
    return fig
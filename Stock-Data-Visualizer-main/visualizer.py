import requests
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
import numpy as np
import time

def createGraph(StartTime, EndTime, DesiredGraph, Company, TimeSeries):
    API_KEY = "H0XQD306IFOZECWX"

    function_map = {
        'intraday': 'TIME_SERIES_INTRADAY',
        'daily': 'TIME_SERIES_DAILY',
        'weekly': 'TIME_SERIES_WEEKLY',
        'monthly': 'TIME_SERIES_MONTHLY'
    }

    output_key_map = {
        'intraday': 'Time Series (5min)',
        'daily': 'Time Series (Daily)',
        'weekly': 'Weekly Time Series',
        'monthly': 'Monthly Time Series'
    }

    base_url = 'https://www.alphavantage.co/query'
    time_series_lower = TimeSeries.lower()

    params = {
        'function': function_map[time_series_lower],
        'symbol': Company.upper(),
        'apikey': API_KEY,
    }

    if time_series_lower == 'intraday':
        params['interval'] = '5min'
        params['outputsize'] = 'compact'   # free tier only supports compact for intraday
        # Update the key BEFORE we use it below
        output_key_map['intraday'] = f'Time Series ({params["interval"]})'
    else:
        params['outputsize'] = 'full'

    try:
        print(f"Fetching {TimeSeries} data for {Company}...")
        response = requests.get(base_url, params=params)
        data = response.json()

        print(f"API response keys: {list(data.keys())}")  # helpful for debugging

        if 'Error Message' in data:
            raise ValueError(f"API Error: {data['Error Message']}")

        if 'Note' in data:
            print(f"API Note: {data['Note']}")
            print("Waiting 60 seconds before retry...")
            time.sleep(60)
            response = requests.get(base_url, params=params)
            data = response.json()

        if 'Information' in data:
            raise ValueError(f"API limit reached: {data['Information']}")

        time_series_key = output_key_map[time_series_lower]

        if time_series_key not in data:
            fallback_key = next((k for k in data.keys() if 'Time Series' in k or 'time series' in k.lower()), None)
            if fallback_key:
                print(f"Warning: Expected key '{time_series_key}' not found. Using '{fallback_key}' instead.")
                time_series_key = fallback_key
            else:
                raise ValueError(
                    f"No time series data found for {Company}. "
                    f"Expected key '{time_series_key}'. "
                    f"Available keys: {list(data.keys())}"
                )

        time_series_data = data[time_series_key]

        df = pd.DataFrame.from_dict(time_series_data, orient='index')
        df.index = pd.to_datetime(df.index)
        df.sort_index(inplace=True)


        column_mapping = {}
        for col in df.columns:
            if 'open' in col.lower():
                column_mapping[col] = 'Open'
            elif 'high' in col.lower():
                column_mapping[col] = 'High'
            elif 'low' in col.lower():
                column_mapping[col] = 'Low'
            elif 'close' in col.lower():
                column_mapping[col] = 'Close'

        df = df.rename(columns=column_mapping)

        for col in ['Open', 'High', 'Low', 'Close']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        df = df.dropna(subset=['Close'])

        start_date = pd.to_datetime(StartTime)
        end_date = pd.to_datetime(EndTime)

        if time_series_lower in ('weekly', 'monthly'):
            end_date = end_date + pd.offsets.MonthEnd(0) if time_series_lower == 'monthly' \
                       else end_date + pd.Timedelta(days=6)

        df = df[(df.index >= start_date) & (df.index <= end_date)]

        if df.empty:
            raise ValueError(
                f"No data found for {Company} in the date range {StartTime} to {EndTime}. "
                f"For weekly data, data points fall on Fridays — try widening your date range."
            )

        print(f"Successfully retrieved {len(df)} data points")

    except Exception as e:
        print(f"Error fetching data: {e}")
        return None
    
    fig, ax = plt.subplots(figsize=(14, 8))

    available_cols = [col for col in ['Open', 'High', 'Low', 'Close'] if col in df.columns]

    if DesiredGraph.lower() == 'line':
        for col in available_cols:
            color = 'blue' if col == 'Close' else \
                    'green' if col == 'Open' else \
                    'red' if col == 'High' else 'orange'
            linestyle = '-' if col == 'Close' else '--'
            linewidth = 2 if col == 'Close' else 1.5
            alpha = 1.0 if col == 'Close' else 0.7

            ax.plot(df.index, df[col],
                    color=color, linewidth=linewidth,
                    linestyle=linestyle, alpha=alpha,
                    label=f'{col} Price')

        if 'High' in df.columns and 'Low' in df.columns:
            ax.fill_between(df.index, df['Low'], df['High'],
                            alpha=0.2, color='gray', label='Daily Range')

    elif DesiredGraph.lower() == 'bar':
        width = 0.6
        x_positions = np.arange(len(df))
        colors = {'Open': 'green', 'High': 'red', 'Low': 'orange', 'Close': 'blue'}

        for i, col in enumerate(available_cols):
            offset = (i - len(available_cols) / 2) * (width / len(available_cols))
            ax.bar(x_positions + offset, df[col],
                   width=width / len(available_cols),
                   label=f'{col} Price',
                   color=colors.get(col, 'gray'),
                   alpha=0.7)

        ax.set_xticks(x_positions)
        ax.set_xticklabels([d.strftime('%Y-%m-%d') for d in df.index], rotation=45)

    ax.set_title(f'{Company} Stock Price - {TimeSeries.title()} Data\n{StartTime} to {EndTime}',
                 fontsize=14, fontweight='bold')
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Price (USD)', fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper left')

    current_price = df['Close'].iloc[-1] if 'Close' in df.columns else 0
    start_price = df['Close'].iloc[0] if 'Close' in df.columns else 0
    price_change = current_price - start_price
    price_change_pct = (price_change / start_price) * 100 if start_price != 0 else 0
    period_high = df['High'].max() if 'High' in df.columns and not df['High'].isna().all() else 0
    period_low = df['Low'].min() if 'Low' in df.columns and not df['Low'].isna().all() else 0

    stats_text = (
        f"Start Price:    ${start_price:.2f}\n"
        f"Current Close:  ${current_price:.2f}\n"
        f"Change:         ${price_change:.2f} ({price_change_pct:.2f}%)\n"
        f"Period High:    ${period_high:.2f}\n"
        f"Period Low:     ${period_low:.2f}"
    )

    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
            fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
            family='monospace')

    plt.tight_layout()
    return fig
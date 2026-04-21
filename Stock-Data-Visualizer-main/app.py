from flask import Flask, render_template, request, session
import os
import sys
from datetime import datetime
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for web
import matplotlib.pyplot as plt
import io
import base64

# Import your existing modules
import api_handler
import visualizer

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Monkey patch visualizer's plt.show() to not block
original_show = plt.show
def patched_show():
    pass  # Don't show the plot window in web environment
plt.show = patched_show

def get_chart_as_base64(fig):
    """Convert matplotlib figure to base64 string for web display"""
    img = io.BytesIO()
    fig.savefig(img, format='png', dpi=100, bbox_inches='tight')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close(fig)
    return plot_url

def load_stock_symbols():
    """Load stock symbols from CSV or use default list"""
    stocks = []
    
    # Try to load from CSV
    try:
        import pandas as pd
        if os.path.exists('stocks.csv'):
            df = pd.read_csv('stocks.csv')
            if 'Symbol' in df.columns:
                stocks = df[['Symbol', 'Name']].to_dict('records')
    except:
        pass
    
    # Default stocks if CSV not found
    if not stocks:
        stocks = [
            {'Symbol': 'AAPL', 'Name': 'Apple Inc.'},
            {'Symbol': 'GOOGL', 'Name': 'Alphabet Inc.'},
            {'Symbol': 'MSFT', 'Name': 'Microsoft Corporation'},
            {'Symbol': 'AMZN', 'Name': 'Amazon.com Inc.'},
            {'Symbol': 'META', 'Name': 'Meta Platforms Inc.'},
            {'Symbol': 'TSLA', 'Name': 'Tesla Inc.'},
            {'Symbol': 'NVDA', 'Name': 'NVIDIA Corporation'},
        ]
    
    return stocks

@app.route('/', methods=['GET', 'POST'])
def index():
    """Main route - uses your existing visualizer.createGraph"""
    stocks = load_stock_symbols()
    time_series_names = api_handler.get_time_series_name_map()
    chart_image = None
    error_message = None
    
    if request.method == 'POST':
        try:
            # Get form data
            symbol = request.form.get('symbol')
            time_series_choice = request.form.get('time_series')
            chart_type = request.form.get('chart_type')
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            
            # Validate dates
            if not start_date or not end_date:
                raise ValueError("Please provide both start and end dates")
            
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            
            if end < start:
                raise ValueError("End date cannot be before start date")
            
            # Use your existing visualizer to create the graph
            # But capture the figure instead of showing it
            print(f"\nGenerating chart for {symbol} from {start_date} to {end_date}")
            print(f"Chart type: {chart_type}, Time series: {time_series_choice}")
            
            # Call your existing function
            fig = visualizer.createGraph(
                StartTime=start_date,
                EndTime=end_date,
                DesiredGraph=chart_type,
                Company=symbol,
                TimeSeries=time_series_choice
            )
            
            # Convert the figure to base64 for web display
            if fig:
                chart_image = get_chart_as_base64(fig)
            else:
                raise ValueError("Failed to generate chart")
            
        except Exception as e:
            error_message = str(e)
            print(f"Error: {error_message}")
    
    return render_template('index.html', 
                         stocks=stocks,
                         time_series_names=time_series_names,
                         chart_image=chart_image,
                         error_message=error_message,
                         form_data=request.form)

if __name__ == '__main__':
    # Check for API key
    api_key = api_handler.get_api_key()
    if not api_key:
        print("WARNING: No API key found. Please set ALPHA_VANTAGE_API_KEY in .env file")
    else:
        print(f"API key loaded successfully")
    
    print("\nStarting Stock Visualizer Web App...")

    app.run(debug=True, host='127.0.0.1', port=5000)
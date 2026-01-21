from datetime import datetime, timedelta
import yfinance as yf

def get_stock_prices(ticker: str, days: int = 30) -> str:
    """
    Fetches historical stock prices for a given ticker.
    """
    ticker = ticker.upper().strip()
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    try:
        stock = yf.Ticker(ticker)
        history = stock.history(start=start_date, end=end_date)
        
        if history.empty:
            return f"Error: No data found for '{ticker}'."
        
        clean_data = history.reset_index()[['Date', 'Close', 'Volume']]
        clean_data['Date'] = clean_data['Date'].dt.strftime('%Y-%m-%d')
        return f"Fetched {len(clean_data)} rows for {ticker}.\n\n{clean_data.to_csv(index=False)}"

    except Exception as e:
        return f"Error fetching market data: {str(e)}"

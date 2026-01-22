from datetime import datetime, timedelta
import yfinance as yf

def get_stock_prices(ticker: str, days: int = 30) -> dict:
    """
    Fetches historical stock prices for a given ticker.
    Returns dict with 'message', 'csv', and 'error' keys.
    """
    ticker = ticker.upper().strip()
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    try:
        stock = yf.Ticker(ticker)
        history = stock.history(start=start_date, end=end_date)
        
        if history.empty:
            return {
                "error": True,
                "message": f"No data found for '{ticker}'",
                "csv": ""
            }
        
        clean_data = history.reset_index()[['Date', 'Close', 'Volume']]
        clean_data['Date'] = clean_data['Date'].dt.strftime('%Y-%m-%d')
        csv_data = clean_data.to_csv(index=False)
        
        return {
            "error": False,
            "message": f"Fetched {len(clean_data)} rows for {ticker}",
            "csv": csv_data
        }

    except Exception as e:
        return {
            "error": True,
            "message": f"Error fetching market data: {str(e)}",
            "csv": ""
        }

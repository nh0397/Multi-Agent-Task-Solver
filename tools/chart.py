import plotly.graph_objects as go
import pandas as pd
import io

def generate_chart(ticker: str, data_csv: str):
    """
    Generates an interactive Plotly chart from CSV data.
    """
    try:
        df = pd.read_csv(io.StringIO(data_csv))
        
        if df.empty:
            return f"Error: No data available to chart for {ticker}"
        
        fig = go.Figure()

        # Check for OHLC data to create a Candlestick chart
        if all(col in df.columns for col in ['Open', 'High', 'Low', 'Close', 'Date']):
            fig.add_trace(go.Candlestick(
                x=df['Date'],
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name=ticker
            ))
            chart_type = "Candlestick"
        elif 'Close' in df.columns and 'Date' in df.columns:
            # Line chart with Close price
            fig.add_trace(go.Scatter(x=df['Date'], y=df['Close'], mode='lines', name=ticker))
            chart_type = "Line"
        else:
            # Try to find any numeric column
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) == 0:
                return f"Error: No numeric data found in CSV for {ticker}"
            
            y_col = numeric_cols[0]
            x_col = df.columns[0]  # Use first column as X
            fig.add_trace(go.Scatter(x=df[x_col], y=df[y_col], mode='lines', name=ticker))
            chart_type = "Line"

        fig.update_layout(
            title=f"{ticker} Analysis ({chart_type})", 
            template="plotly_dark",
            xaxis_title="Date",
            yaxis_title="Price"
        )
        return fig
    except Exception as e:
        return f"Error creating chart: {str(e)}"


def generate_comparison_chart(tickers_data: dict):
    """
    Generates a comparison chart for multiple tickers on the same graph.
    
    Args:
        tickers_data: Dict of {ticker: csv_data}
    
    Returns:
        Plotly figure with all tickers overlaid
    """
    try:
        fig = go.Figure()
        
        for ticker, data_csv in tickers_data.items():
            df = pd.read_csv(io.StringIO(data_csv))
            
            if df.empty:
                continue
            
            # Use Close price for comparison
            if 'Close' in df.columns and 'Date' in df.columns:
                fig.add_trace(go.Scatter(
                    x=df['Date'], 
                    y=df['Close'], 
                    mode='lines', 
                    name=ticker
                ))
        
        if len(fig.data) == 0:
            return "Error: No valid data to compare"
        
        fig.update_layout(
            title=f"Stock Comparison: {', '.join(tickers_data.keys())}", 
            template="plotly_dark",
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            hovermode='x unified'
        )
        return fig
    except Exception as e:
        return f"Error creating comparison chart: {str(e)}"

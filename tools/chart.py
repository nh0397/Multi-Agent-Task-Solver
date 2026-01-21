import plotly.graph_objects as go
import pandas as pd
import io

def generate_chart(ticker: str, data_csv: str):
    """
    Generates an interactive Plotly chart from CSV data.
    """
    try:
        df = pd.read_csv(io.StringIO(data_csv))
        fig = go.Figure()

        # Check for OHLC data to create a Candlestick chart
        if all(col in df.columns for col in ['Open', 'High', 'Low', 'Close']):
            fig.add_trace(go.Candlestick(
                x=df['Date'],
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name=ticker
            ))
            chart_type = "Candlestick"
        else:
            # Fallback to Line chart (Close or first numeric column)
            y_col = 'Close' if 'Close' in df.columns else df.select_dtypes(include=['number']).columns[0]
            fig.add_trace(go.Scatter(x=df['Date'], y=df[y_col], mode='lines', name=ticker))
            chart_type = "Line"

        fig.update_layout(title=f"{ticker} Analysis ({chart_type})", template="plotly_dark")
        return fig
    except Exception as e:
        return f"Error creating chart: {str(e)}"

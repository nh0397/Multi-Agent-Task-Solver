"""
Test script for chart generation
"""
from tools.market import get_stock_prices
from tools.chart import generate_chart

# Test 1: Fetch data
print("=" * 60)
print("TEST 1: Fetching market data for NVDA")
print("=" * 60)

result = get_stock_prices("NVDA", days=30)

if result['error']:
    print(f"❌ ERROR: {result['message']}")
    exit(1)

print(f"✓ {result['message']}")
print("\nCSV Data (first 500 chars):")
print(result['csv'][:500])
print("\n")

# Test 2: Generate chart
print("=" * 60)
print("TEST 2: Generating chart from pure CSV")
print("=" * 60)

# Pass pure CSV to chart (this is what supervisor does now)
fig = generate_chart("NVDA", result['csv'])

if isinstance(fig, str):
    print(f"❌ ERROR: {fig}")
else:
    print("✓ Chart generated successfully!")
    print(f"Chart type: {type(fig).__name__}")
    
    # Save to HTML and open
    fig.write_html("test_chart.html")
    print("\n✓ Chart saved to test_chart.html")
    print("Opening in browser...")
    
    import webbrowser
    webbrowser.open("test_chart.html")

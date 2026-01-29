import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="Wintermute Whale Watch", layout="wide")
load_dotenv()
ETH_KEY = os.getenv('ETHERSCAN_API_KEY')
WHALE_ADDR = "0xdbf5e9c5206d0db70a90108bf936da60221dc080" # Wintermute

# 2. Sidebar & Data Fetching
st.sidebar.title("Controls")
offset = st.sidebar.slider("Transactions to Scan", 10, 200, 100)

@st.cache_data(ttl=300) # Refresh data every 5 mins
def get_data(api_key, limit):
    url = "https://api.etherscan.io/v2/api"
    params = {"chainid": "1", "module": "account", "action": "tokentx", 
              "address": WHALE_ADDR, "offset": limit, "sort": "desc", "apikey": api_key}
    res = requests.get(url, params=params).json()
    if res.get('status') == '1':
        df = pd.DataFrame(res['result'])
        df['datetime'] = pd.to_datetime(df['timeStamp'].astype(int), unit='s')
        df['amount'] = df.apply(lambda x: float(x['value']) / (10**int(x['tokenDecimal'])), axis=1)
        return df[['datetime', 'from', 'to', 'amount', 'tokenSymbol', 'hash']]
    return pd.DataFrame()

# 3. Execution
st.title("🐋 Wintermute 2026: Real-Time Liquidity Pulse")
st.markdown(f"**Tracking Wallet:** `{WHALE_ADDR}`")

df = get_data(ETH_KEY, offset)

if not df.empty:
    # Top Level Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Unique Assets Found", df['tokenSymbol'].nunique())
    col2.metric("Total Transactions", len(df))
    col3.metric("Top Asset Moved", df['tokenSymbol'].mode()[0])

    # Plotly Chart
    fig = px.scatter(df, x="datetime", y="amount", color="tokenSymbol", 
                     size="amount", log_y=True, template="plotly_dark",
                     title="Whale Transaction Galaxy (Log Scale)")
    st.plotly_chart(fig, use_container_width=True)

    # Interactive Table
    st.subheader("Detailed Transaction Ledger")
    st.dataframe(df, use_container_width=True)
else:
    st.error("Could not fetch data. Check your API Key.")


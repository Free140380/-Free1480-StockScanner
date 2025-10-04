import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import datetime as dt
import time

# ==========================================
# CONFIGURAZIONE BASE
# ==========================================
PASSWORD = "marketlive"  # 🔐 password demo
WATCHLIST = ["AAPL", "MSFT", "GOOG"]
INTERVAL = "5m"
LOOKBACK = "5d"

# ==========================================
# PAGINA E ACCESSO
# ==========================================
st.set_page_config(page_title="Free1480 Stock Scanner Demo", layout="centered", page_icon="📈")

st.markdown(
    "<h2 style='text-align:center;'>📊 Real-Time Stock Scanner – Private Demo</h2>",
    unsafe_allow_html=True
)
st.markdown(
    "<p style='text-align:center;color:gray;'>Demo access – ask <b>Free1480</b> for the password.</p>",
    unsafe_allow_html=True
)

# Campo password e nome utente
username = st.text_input("Enter your name (optional):", placeholder="Trader")
password_input = st.text_input("Enter demo password:", type="password")

if password_input != PASSWORD:
    st.warning("🔒 Access denied. Please request the demo password via Freelancer message.")
    st.stop()

# Benvenuto personalizzato
st.success(f"✅ Welcome {username if username else 'Trader'}! Access granted to Free1480 demo.")
st.markdown("<hr>", unsafe_allow_html=True)

# ==========================================
# FUNZIONI TECNICHE
# ==========================================
def compute_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def get_indicators(ticker: str):
    try:
        df = yf.download(ticker, period=LOOKBACK, interval=INTERVAL, progress=False, auto_adjust=False)
    except Exception as e:
        st.error(f"Error downloading {ticker}: {e}")
        return None

    if df.empty:
        return None

    df["rsi"] = compute_rsi(df["Close"])
    df["ema_fast"] = df["Close"].ewm(span=20, adjust=False).mean()
    df["ema_slow"] = df["Close"].ewm(span=50, adjust=False).mean()

    rsi_val = float(df["rsi"].iloc[-1])
    ema_fast = float(df["ema_fast"].iloc[-1])
    ema_slow = float(df["ema_slow"].iloc[-1])

    signal = ""
    if not np.isnan(rsi_val):
        if rsi_val < 30:
            signal += "RSI Oversold "
        elif rsi_val > 70:
            signal += "RSI Overbought "

    if not np.isnan(ema_fast) and not np.isnan(ema_slow):
        if ema_fast > ema_slow:
            signal += "Bullish EMA Cross"
        elif ema_fast < ema_slow:
            signal += "Bearish EMA Cross"

    return {
        "Ticker": ticker,
        "RSI": round(rsi_val, 2),
        "EMA20": round(ema_fast, 2),
        "EMA50": round(ema_slow, 2),
        "Signal": signal if signal else "-"
    }

# ==========================================
# INTERFACCIA STREAMLIT
# ==========================================
placeholder = st.empty()

while True:
    data = []
    for ticker in WATCHLIST:
        info = get_indicators(ticker)
        if info:
            data.append(info)

    if data:
        df_display = pd.DataFrame(data)
        df_display = df_display[["Ticker", "RSI", "EMA20", "EMA50", "Signal"]]
        with placeholder.container():
            st.dataframe(df_display, use_container_width=True)
            st.write(f"⏱ Last update: {dt.datetime.now().strftime('%H:%M:%S')}")
            st.caption("Demo by Free1480 – All rights reserved.")
    else:
        st.warning("No data available at the moment.")

    time.sleep(60)

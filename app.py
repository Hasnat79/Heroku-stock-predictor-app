import streamlit as st
from datetime import date
import datetime

import yahoo_fin.stock_info as si

import yfinance as yf


from prophet import Prophet
from prophet.plot import plot_plotly
from plotly import graph_objs as go

START = "2010-01-01"
TODAY = date.today().strftime("%Y-%m-%d")

st.title("Stock Predictor Web App")

@st.cache
def load_all_tickers():
    return tuple(si.tickers_dow()+si.tickers_sp500()+si.tickers_nasdaq())

load_ticker_state=st.text("Loading tickers...")
stocks = load_all_tickers()
load_ticker_state.text("Loading tickers... done!")

selected_stock=st.selectbox("Select dataset for prediction",stocks)



@st.cache
def load_data(ticker):
    data=yf.download(ticker,START,TODAY)
    data.reset_index(inplace=True)
    return data

data_load_state=st.text("Loading data...")
data=load_data(selected_stock)
data_load_state.text("loading data... done")

st.subheader('Raw data')
st.write(data.tail())

def plot_raw_data():
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=data['Date'],y=data['Open'],name='stock_open'))
    fig.add_trace(go.Scatter(x=data['Date'],y=data['Close'],name='stock_close'))
    fig.layout.update(title_text="Time Series Data",xaxis_rangeslider_visible=True)
    st.plotly_chart(fig)

plot_raw_data()

#Forecasting
st.subheader('Forecasting Stock Price')

n_years=st.slider("How many years of prediction you want?",1,5)
period = n_years*365

df_train=data[['Date','Close']]
df_train=df_train.rename(columns={"Date":"ds","Close":"y"})

forecast_state=st.text("fitting the prophet model...")
m=Prophet()
m.fit(df_train)
future=m.make_future_dataframe(periods=period)
forecast=m.predict(future)

forecast_state.text("fitting the prophet model... done!")

st.subheader(f"Future stock prices of {selected_stock}")
st.write(forecast)

st.subheader(f'Future stock prices of {selected_stock}: interactive graph')
fig1=plot_plotly(m,forecast)
st.plotly_chart(fig1)

st.subheader('See the trends on year,month, week basis')
fig2=m.plot_components(forecast)
st.write(fig2)


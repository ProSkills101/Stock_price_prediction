import numpy as np
import pandas as pd
import pandas_datareader as pdr
from pandas_datareader import data as pdr
import yfinance as yf
yf.pdr_override()
import pandas_ta as ta
#import seaborn as sns
import datetime as datetime
from dash import Dash, dash_table, dcc, html, Input, Output
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.preprocessing import MinMaxScaler
from jupyter_dash import JupyterDash

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css',
                        'https://cdn.datatables.net/1.10.21/css/jquery.dataTables.min.css']
app = JupyterDash(__name__, external_stylesheets=external_stylesheets)

app.title='Stock Visualization'
app.layout = html.Div(children=[
    html.H1('Stock Visualization Dashboard'),
    html.H4('Please enter the stock name'),
    dcc.Input(id='input', value='TSLA', type='text'),
    html.Div(id='output-graph'),
    html.Hr(),  # Add a horizontal line to separate the chart and table
    html.H4('Oscillators Table'),
    dash_table.DataTable(id='oscillator-table',
                         columns=[{'name': 'Oscillator', 'id': 'Oscillator'},
                                  {'name': 'Value', 'id': 'Value'},
                                  {'name': 'Action', 'id': 'Action'}] ),
    html.H4('Moving Averages Table'),
    dash_table.DataTable(id='ma-table',
                         columns=[{'name': 'Moving Averages', 'id': 'Moving Averages'},
                                  {'name': 'Value', 'id': 'Value'},
                                  {'name': 'Action', 'id': 'Action'}] ),
    html.H6("Note: There are no overall evaluations for moving averages as it highly depends on the investent timeframe.")
])

@app.callback(
    Output(component_id='output-graph', component_property='children'),
    Output(component_id='oscillator-table', component_property='data'),  # Updated ID
    Output(component_id='ma-table', component_property='data'),  # Updated ID
    Input(component_id='input', component_property='value'),
)

def update_value(input_sid, n_submit): 
    # Reads stock prices from 1st January 2022 
    #start = dt.datetime(2022, 1, 1)  
    #end = dt.datetime.now() 
    sid = input_sid #"TSLA"
    n_year = 0.5
    end_date = datetime.datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.datetime.now()- datetime.timedelta(days=n_year*365)).strftime('%Y-%m-%d')
    df = pdr.get_data_yahoo(sid, start=start_date, end=end_date)

    # Define periods
    k_period = 14
    d_period = 3
    # Adds a "n_high" column with max value of previous 14 periods
    df['n_high'] = df['High'].rolling(k_period).max()
    # Adds an "n_low" column with min value of previous 14 periods
    df['n_low'] = df['Low'].rolling(k_period).min()
    # Uses the min/max values to calculate the %k (as a percentage)
    df['%k'] = (df['Close'] - df['n_low']) * 100 / (df['n_high'] - df['n_low'])
    # Uses the %k to calculates a SMA over the past 3 values of %k
    df['%d'] = df['%k'].rolling(d_period).mean()

    df.ta.stoch(high='high', low='low', k=14, d=3, append=True)

    # Avoid case-sensitive issues for accessing data.
    # Optional if using pandas_ta
    df.columns = [x.lower() for x in df.columns]

    # Add scaler to fit volume inside primary chart
    # Maximum volume should be one-fifths of maximum price
    # Note: Value mentioned above is viable for change.

    #scaler = MinMaxScaler(feature_range=(0,df['High'].rolling(200).max()))

    # Create our primary chart
    # the rows/cols arguments tell plotly we want two figures
    fig = make_subplots(rows=3, cols=1)  
    # Create our Candlestick chart with an overlaid price line
    fig.append_trace(
        go.Candlestick(
            x=df.index,
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            increasing_line_color='red',
            decreasing_line_color='green',
            showlegend=False
        ), row=1, col=1  # <------------ upper chart
    )
    # price Line
    fig.append_trace(
        go.Scatter(
            x=df.index,
            y=df['open'],
            line=dict(color='black', width=1),
            name='open',
        ), row=1, col=1  # <------------ upper chart
    )
    # Fast Signal (%k)
    fig.append_trace(
        go.Scatter(
            x=df.index,
            y=df['%k'],
            line=dict(color='red', width=2),
            name='fast',
        ), row=3, col=1  #  <------------ lower chart
    )
    # Slow signal (%d)
    fig.append_trace(
        go.Scatter(
            x=df.index,
            y=df['%d'],
            line=dict(color='cyan', width=2),
            name='slow'
        ), row=3, col=1  #<------------ lower chart
    )
    fig.append_trace(
        go.Scatter(
            x=df.index,
            y=df['volume'],
            line=dict(color='black', width=2),
            name='volume'
        ), row=2, col=1  
    )
    # Extend our y-axis a bit
    fig.update_yaxes(range=[-10, 110], row=3, col=1)
    fig.update_xaxes(showticklabels=False) # hide all the xticks
    fig.update_xaxes(showticklabels=True, row=3, col=1)
    # Add upper/lower bounds
    fig.add_hline(y=0, col=1, row=3, line_color="#666", line_width=2)
    fig.add_hline(y=100, col=1, row=3, line_color="#666", line_width=2)
    # Add overbought/oversold
    fig.add_hline(y=20, col=1, row=3, line_color='#336699', line_width=2, line_dash='dash')
    fig.add_hline(y=80, col=1, row=3, line_color='#336699', line_width=2, line_dash='dash')
    # Make it pretty
    layout = go.Layout(
        plot_bgcolor='#efefef',
        # Font Families
        font_family='Monospace',
        font_color='#000000',
        font_size=20,
        xaxis=dict(
            rangeslider=dict(
                visible=False
            )
        ),
        title_text=sid
    )
    fig.update_layout(layout)   

    # Table creation
    os_actions = []
    os_score = 0

    rsi = ta.rsi(df['close']) # RSI
    latest_rsi = round(rsi.iloc[-1], 2)
    if (latest_rsi > 80): os_actions.append("Strong sell"); os_score -= 2
    elif (latest_rsi > 60): os_actions.append("Sell"); os_score -= 1
    elif (latest_rsi > 40): os_actions.append("Neutral"); 
    elif (latest_rsi > 20): os_actions.append("Buy"); os_score += 1
    else: os_actions.append("Strong buy"); os_score += 2

    latest_stoch = round(df['%k'].iloc[-1], 2) # Stochastic, referenced from previous data table
    if (latest_stoch > 80): os_actions.append("Sell"); os_score -= 1
    if (latest_stoch < 20): os_actions.append("Buy"); os_score += 1
    else: os_actions.append("Neutral")

    willr = ta.willr(df['high'], df['low'], df['close']) # Williams Percent Range, 14 days
    latest_willr = round(willr.iloc[-1], 2)
    if (latest_willr > -20): os_actions.append("Sell"); os_score -= 1
    if (latest_willr < -80): os_actions.append("Buy"); os_score += 1
    else: os_actions.append("Neutral")

    macd = ta.macd(df['close']) # MACD
    latest_macd = round(macd.iloc[-1], 2)
    float_macd = float(str(latest_macd)[61:65])
    if (float_macd >= 0.15): os_actions.append("Strong buy"); os_score += 2
    elif (float_macd >= 0.05):  os_actions.append("Buy"); os_score += 1
    elif (float_macd <= -0.15): os_actions.append("Strong sell"); os_score -= 2
    elif (float_macd <= -0.05): os_actions.append("Sell"); os_score -= 1
    else: os_actions.append("Neutral")

    cci = ta.cci(df['high'], df['low'], df['close']) # CCI
    latest_cci = round(cci.iloc[-1], 2)

    if (latest_cci > 100): os_actions.append("Sell"); os_score -= 1
    elif (latest_cci < -100):  os_actions.append("Buy"); os_score += 1
    else: os_actions.append("Neutral")

    adx = ta.adx(df['high'], df['low'], df['close']) # ADX
    latest_adx = round(adx.iloc[-1], 2)
    float_adx = float(str(latest_adx)[8:15])
    if (os_score == 0 or abs(float_adx) < 25): os_actions.append("Neutral")
    elif (os_score > 0):
        if (float_adx > 50): os_actions.append("Strong buy"); os_score += 2
        else: os_actions.append("Buy"); os_score += 1
    else:
        if (float_adx > 50): os_actions.append("Strong sell"); os_score -= 2
        else: os_actions.append("Sell"); os_score -= 1

    if (os_score >= 5): os_action = "Strong buy"
    elif (os_score >= 3): os_action = "Buy"
    elif (os_score <= -5): os_action = "Strong sell"
    elif (os_score <= -3): os_action = "Sell"
    else: os_action = "Neutral"

    # Define the DataTable component
    oscillator_data = pd.DataFrame({
        'Oscillator': ['RSI', 'Stochastic', 'Williams Percent Range', 'MACD', 'CCI', 'ADX'],  # Add more indicators as needed
        'Value': [latest_rsi, latest_stoch, latest_willr, float_macd, latest_cci, float_adx], 
        'Action': os_actions 
    })
    oscillator_data = oscillator_data.sort_values("Oscillator", ascending = True)
    oscillator_data.loc[6] = ['Overall', os_score , os_action]

    sma_10 = ta.sma(df['close'], length=10, append=False)
    latest_sma_10 = round(sma_10.iloc[-1], 2)
    sma_20 = ta.sma(df['close'], length=20, append=False)
    latest_sma_20 = round(sma_20.iloc[-1], 2)
    sma_50 = ta.sma(df['close'], length=50, append=False)
    latest_sma_50 = round(sma_50.iloc[-1], 2)
    sma_100 = ta.sma(df['close'], length=100, append=False)
    latest_sma_100 = round(sma_100.iloc[-1], 2)
    ema_10 = ta.ema(df['close'], length=10, append=False)
    latest_ema_10 = round(ema_10.iloc[-1], 2)
    ema_20 = ta.ema(df['close'], length=20, append=False)
    latest_ema_20 = round(ema_20.iloc[-1], 2)
    ema_50 = ta.ema(df['close'], length=50, append=False)
    latest_ema_50 = round(ema_50.iloc[-1], 2)
    ema_100 = ta.ema(df['close'], length=100, append=False)
    latest_ema_100 = round(ema_100.iloc[-1], 2)
    hma = ta.hma(df['close'], length=16, add_to_input=False)
    latest_hma = round(hma.iloc[-1], 2)
    
    # Gives recommendations to buy or sell based on relationship between Moving average and Closing price
    values = [latest_sma_10, latest_ema_10, latest_sma_20, latest_ema_20, latest_sma_50, 
                  latest_ema_50, latest_sma_100, latest_ema_100, latest_hma] 
    ma_actions = []
    close = df['close'].iloc[-1]
    for ma in values:
        diff = ((close-ma)/ma)
        if (diff >= 0.05): ma_actions.append("Strong buy")
        elif (diff >= 0.02):  ma_actions.append("Buy")
        elif (diff <= -0.05): ma_actions.append("Strong sell")
        elif (diff <= -0.02): ma_actions.append("Sell")
        else: ma_actions.append("Neutral")

    ma_data = pd.DataFrame({
        'Moving Averages': ['SMA (10 days)', 'EMA (10 days)', 'SMA (20 days)', 'EMA (20 days)', 
                            'SMA (50 days)', 'EMA (50 days)', 'SMA (100 days)', 'EMA (100 days)', 
                            'Hull Moving Average'], 
        'Value': values, 'Action': ma_actions
    })
    
    return dcc.Graph(id='demo', figure=fig), oscillator_data.to_dict('records'), ma_data.to_dict('records')

#ADDRESS = '140.113.195.226'
if __name__ == '__main__':
    app.run_server(debug=True, port=8052)   

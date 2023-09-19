import numpy as np
import pandas as pd
import pandas_datareader as pdr
from pandas_datareader import data as pdr
import yfinance as yf
yf.pdr_override()
import pandas_ta as ta
#import seaborn as sns
import datetime as datetime
from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.preprocessing import MinMaxScaler
from jupyter_dash import JupyterDash

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = JupyterDash(__name__, external_stylesheets=external_stylesheets)

app.title='Stock Visualization'
app.layout = html.Div(children=[
    html.H1('Stock Visualization Dashboard'),
    html.H4('Please enter the stock name'),
    dcc.Input(id='input', value='TSLA', type='text'),
    html.Div(id='output-graph')
    ])


@app.callback(
    Output(component_id='output-graph', component_property='children'),
    Input(component_id='input', component_property='value')
)

def update_value(input_sid): 
    # Reads stock prices from 1st January 2022 
    #start = dt.datetime(2022, 1, 1)  
    #end = dt.datetime.now() 
    sid = input_sid #"TSLA"
    n_year = 0.5
    end_date = datetime.datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.datetime.now()- datetime.timedelta(days=n_year*365)).strftime('%Y-%m-%d')
    df = pdr.get_data_yahoo(sid, start=start_date, end=end_date)

    # Read stock data from yahoo's finance API from start to end  
    #df = web.DataReader(input_data, 'yahoo', start, end) 

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

    return dcc.Graph(id='demo', figure=fig)

#ADDRESS = '140.113.195.226'
if __name__ == '__main__':
    app.run_server(debug=True, port=8052)   

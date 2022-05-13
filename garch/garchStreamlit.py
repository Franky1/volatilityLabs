import streamlit as st
from arch.univariate import ConstantMean, GARCH, Normal
import plotly.express as px
import psycopg2
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

plt.style.use('ggplot')

def garchFigures(secretDict, timestampLower, timestampUpper):

    dbUsername = secretDict['dbUsername']
    dbPassword = secretDict['dbPassword']
    dbHostname = secretDict['dbHostname']
    database = secretDict['database']

    query = queryGet(0, (timestampLower, timestampUpper))
    df = dfNormalize(dbQuery(dbUsername, dbPassword, dbHostname, database, query))
    prices = df['price'].values
    datetimes = df['datetime'].values

    returns = np.divide(np.diff(prices), prices[1:])

    am = ConstantMean(returns)
    am.volatility = GARCH(1, 0, 1)
    am.distribution = Normal()
    res=am.fit()

    fig = px.line(x=datetimes[:-1], y = res.conditional_volatility)
    fig.update_layout(title='GARCH(1,1) Model', 
                      xaxis_title="Datetime", 
                      yaxis_title="Volatility")
    
    return fig, None

def dfNormalize(df):
    
    df1 = df.copy()
    df1.set_index('datetime', inplace=True)
    df1 = df1.asfreq(freq='S', method='pad')
    df1.reset_index(inplace=True)
    df1['datetime'] = df1['datetime'].apply(lambda x: x.replace(microsecond=0))
    
    return df1

def dbQuery(dbUsername, dbPassword, dbHostname, database, query):

    try:
        conn = psycopg2.connect (dbname = database,
                                 user = dbUsername,
                                 password = dbPassword,
                                 host = dbHostname,
                                 connect_timeout = 10)

        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        cur.close()
        conn.close()

        df = pd.DataFrame(rows)
        df.columns = ['datetime', 'price']
        df['price'] = df['price'].astype('float')
        return df

    except:
        print("Some problem")
        return("Some problem")


def queryGet(index, parameters):
    if index == 0:
        query = """SELECT timestamp, price from trade_pairs where symbol::text like 'ETH%%' 
                   and exchange::text like 'coinbase'
                   and timestamp >= '%s' and timestamp < '%s' order by timestamp asc""" % parameters
    
    return query
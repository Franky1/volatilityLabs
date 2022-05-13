import streamlit as st
import plotly.express as px
import psycopg2
import pandas as pd
import numpy as np

def skewFigures(secretDict, timestampLower, timestampUpper):

    dbUsername = secretDict['dbUsername']
    dbPassword = secretDict['dbPassword']
    dbHostname = secretDict['dbHostname']
    database = secretDict['database']

    query = queryGet(0, (timestampLower, timestampUpper))
    #df = dfNormalize(dbQuery(dbUsername, dbPassword, dbHostname, database, query))
    fig = px.line(x=range(10), y = range(10))
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

        rows = [(a, b, c, float(d), float(e)) for (a, b, c, d, e) in rows]
        df = pd.DataFrame(rows)
        df.columns = ['datetime', 'optionType', 'symbol', 'markIV', 'delta']
        return df

    except:
        print("Some problem")
        return("Some problem")

def queryGet(index, parameters):
    if index == 0:
        query = """ SELECT timestamp, "optionType", symbol, "markIV", delta
                   from trade_options where symbol::text like 'ETH%%' and exchange::text like 'deribit'
                   and timestamp >= '%s' and timestamp < '%s' order by timestamp asc""" % parameters
    
    return query
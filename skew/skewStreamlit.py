#%%
import streamlit as st
import plotly.express as px
import psycopg2
import pandas as pd
import numpy as np
import datetime

def skewFigures(secretDict, timestampLower, timestampUpper):

    dbUsername = secretDict['dbUsername']
    dbPassword = secretDict['dbPassword']
    dbHostname = secretDict['dbHostname']
    database = secretDict['database']

    #query = queryGet(0, (timestampLower, timestampUpper))
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
        rows = [(a.split('-')[1], float(b), float(c), d, float(e)) for a,b,c,d,e in rows]
        df = pd.DataFrame(rows)
        return df

    except:
        print("Some problem")
        return("Some problem")

def queryGet(index, parameters):
    if index == 0:
        query = """ SELECT timestamp, "optionType", symbol, "markIV", delta
                   from trade_options where symbol::text like 'ETH%%' and exchange::text like 'deribit'
                   and timestamp >= '%s' and timestamp < '%s' order by timestamp asc""" % parameters
    elif index == 1:
        query = '''
            SELECT
            trade_options.symbol, trade_options."markIV", "strikePrice", "optionType", delta
            FROM
            (
                SELECT 
                symbol, MAX(timestamp) AS timestamp
                FROM 
                trade_options
                WHERE 
                now() < "expirationDate" 
                AND 
                asset = 'ETH'
                GROUP BY 
                symbol
            ) as latest_symbols
            INNER JOIN
            trade_options
            ON
            trade_options.timestamp = latest_symbols.timestamp AND trade_options.symbol = latest_symbols.symbol
            ORDER BY latest_symbols.timestamp ASC
            ;
        '''
    
    return query

#%%

    
dbUsername = "harper"
dbPassword = "VbeGd95Fmejj6RvAttunvr06rvaGHTmO"
dbHostname = "vg-ue2-stageplatform-harper-db.cluster-cceymqxp5c9l.us-east-2.rds.amazonaws.com"
database = "volatility_labs"

query = queryGet(1, None)
df = dbQuery(dbUsername, dbPassword, dbHostname, database, query)
df.columns = ['expiration', 'iv', 'strike', 'type', 'delta']

#%%
grouped = df.groupby(df.expiration)
allDataframes = {i:grouped.get_group(i) for i in list(set(df.expiration.values))}

# %%
def skewGet(dfCallPut, delta):
    grouped = dfCallPut.groupby(dfCallPut.type)
    callFrame = grouped.get_group('call')
    putFrame = grouped.get_group('put')
    callIndex = callFrame['delta'].sub(delta).abs().idxmin()
    putIndex = putFrame['delta'].sub(-delta).abs().idxmin()

    callIV = callFrame.loc[callIndex]['iv']
    putIV = putFrame.loc[putIndex]['iv']

    callAtTheMoneyIndex = callFrame['delta'].sub(.5).abs().idxmin()
    putAtTheMoneyIndex = putFrame['delta'].sub(-.5).abs().idxmin()

    atTheMoneyIV = (callFrame.loc[callAtTheMoneyIndex]['iv'] + putFrame.loc[putAtTheMoneyIndex]['iv'])/2
    skew = 100 * (putIV - callIV)/atTheMoneyIV
    return skew

temp = list(allDataframes.values())[0]
skewGet(temp, .25)

# %%

def symbolToDatetime(optionDateSymbol):

    monthToNumber = {'JAN':1, 'FEB':2, 'MAR':3, 'APR':4, 'MAY':5, 'JUN':6, 'JUL':7, 'AUG':8, 'SEP':9, 'OCT':10, 'NOV':11, 'DEC':12 }

    day = int(optionDateSymbol[:-5])
    month = int(monthToNumber[optionDateSymbol[-5:-2]])
    year = int('20' + optionDateSymbol[-2:])   
    thisDatetime = datetime.datetime(year, month, day)
    return thisDatetime
        
symbolToDatetime('24JUN22')




# %%

def optionSymbolsTargetSort(optionSymbolList, targetDate):

    datetimeList = sorted([symbolToDatetime(i) for i in optionSymbolList])

    booleanList = list(map(lambda k: k > targetDate, datetimeList))
    if True in booleanList:
         indexOfBeforeOption = booleanList.index(True)
    else:
        indexOfBeforeOption = None
    return datetimeList, indexOfBeforeOption

daysInFuture = 40
targetDate = datetime.datetime.now() + datetime.timedelta(days=daysInFuture)
optionSymbolsTargetSort(list(set(df.expiration)), targetDate)

# %%

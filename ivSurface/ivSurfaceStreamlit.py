import plotly.graph_objects as go
import numpy as np
import datetime
from scipy import interpolate
import psycopg2

def ivSurfaceFigures(secretDict, timestampLower, timestampUpper):
    dbUsername = secretDict['dbUsername']
    dbPassword = secretDict['dbPassword']
    dbHostname = secretDict['dbHostname']
    database = secretDict['database']

    ivData = dbQuery(dbUsername, dbPassword, dbHostname, database, timestampLower, timestampUpper)
    fig = ivSurface(ivData)
    return fig, None


def dbQuery(dbUsername, dbPassword, dbHostname, database, timestampLower, timestampUpper):

    try:
        conn = psycopg2.connect (dbname = database,
                                 user = dbUsername,
                                 password = dbPassword,
                                 host = dbHostname,
                                 connect_timeout = 10)
        
        query = queryList(0, None)
        #query = queryList(1, (timestampLower, timestampUpper))

        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        cur.close()
        conn.close()

        rows = [(a, float(b)) for (a, b) in rows]
        return rows

    except:
        print("Some problem")
        return("Some problem")

def interpolateOptions(x,y,z):

    xx = np.linspace(min(x), max(x), 200)
    yy = np.linspace(min(y), max(y), 200)

    X,Y = np.meshgrid(xx, yy)
    Z = interpolate.griddata((x, y), z, (X,Y), method='cubic')

    return X,Y,Z


def ivSurface(options):
    x,y,z = [],[],[]
    optionItems = [i for i in options if i[0][-1]=='C']
    secondsPerDay = 60 * 60 * 24

    monthToNumber = {'JAN':1, 'FEB':2, 'MAR':3, 'APR':4, 'MAY':5, 'JUN':6, 'JUL':7, 'AUG':8, 'SEP':9, 'OCT':10, 'NOV':11, 'DEC':12 }
    for symbol, iv in optionItems:
        thisDate = symbol.split('-')[1]
        day = int(thisDate[:-5])
        year = int('20' + thisDate[-2:])
        month = int(monthToNumber[thisDate[-5:-2]])
        daysToExpiration = (datetime.datetime(year, month, day, 8) - datetime.datetime.utcnow()).total_seconds()/secondsPerDay
        
        strike = float(symbol.split('-')[-2])
        if strike <= 10000:
            x.append(strike)
            y.append(daysToExpiration)
            z.append(iv)
        
    x = np.array(x)
    y = np.array(y)
    z = np.array(z)

    xx,yy,zz = interpolateOptions(x,y,z)

    fig = go.Figure(data=[go.Surface(z=zz, x=xx, y=yy)])
    fig.update_layout(title='Realtime Implied Volatility Surface for Deribit ETH Options', autosize=False, width=800, height=800)
    fig.update_layout(scene = dict(
                        xaxis_title='Strike Price',
                        yaxis_title='Days to Expiration',
                        zaxis_title='Implied Volatility'))
    return fig

def queryList(index, parameters):

    if index == 0:
        query = '''
            SELECT
            trade_options.symbol, trade_options."markIV"
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
    elif index == 1:
        query = """ SELECT DISTINCT ON (symbol) symbol, "markIV"
                    from trade_options where symbol::text like 'ETH%%' and exchange::text like 'deribit'
                    and timestamp >= '%s' and timestamp < '%s' order by symbol, timestamp desc""" % parameters

    return query




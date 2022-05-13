import streamlit as st
import matplotlib.pyplot as plt
import datetime
import os, sys

vecmPath = os.path.dirname(__file__) + '/../garch'
sys.path.append(vecmPath)
import garchStreamlit as garch

plt.style.use('ggplot')

SECONDSBACKTORETRIEVE = 3600

def render(secretDict):
    garchBlurb = '''
    The GARCH family of statistical models incorporate the empirical fact that volatility
    is variable over time and exhibits clustering, i.e. periods of high volatility tend to follow
    periods of high volatilty and similarly with low volatility.  Below we show a graph of the
    volatility of ETH spot prices on Coinbase using a GARCH(1,1) model.
    '''
    st.write(garchBlurb)

    timestampUpper = datetime.datetime.now(datetime.timezone.utc)
    timestampLower = timestampUpper - datetime.timedelta(seconds=SECONDSBACKTORETRIEVE)

    fig0, temp = garch.garchFigures(secretDict, timestampLower, timestampUpper)
    st.plotly_chart(fig0, use_container_width=True)

    if temp is not None:
        st.write(temp)
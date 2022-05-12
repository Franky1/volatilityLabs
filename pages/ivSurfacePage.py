import streamlit as st
import matplotlib.pyplot as plt
import datetime
import os, sys

vecmPath = os.path.dirname(__file__) + '/../ivSurface'
sys.path.append(vecmPath)
import ivSurfaceStreamlit as ivSurface

plt.style.use('ggplot')

SECONDSBACKTORETRIEVE = 3600

def render(secretDict):
    surfaceBlurb = '''
    Given the current market price for an option on an underlying asset, the "implied volalatility" is the
    value for the volatility variable which, when used in the Black-Scholes model, yields the market price.
    Theory dictates that the implied volatility should be constant over expiration dates and strike prices.
    Therefore if we plot implied volatilty as a function of expiration and strike we would expect to see a flat surface.
    However practice does not conform to theory as revealed below in a 3-d surface plot of implied volatility. 
    There is an extensive literature investigating the reasons for this departure from theory.
    '''
    st.write(surfaceBlurb)

    timestampUpper = datetime.datetime.now(datetime.timezone.utc)
    timestampLower = timestampUpper - datetime.timedelta(seconds=SECONDSBACKTORETRIEVE)

    fig0, temp = ivSurface.ivSurfaceFigures(secretDict, timestampLower, timestampUpper)
    st.plotly_chart(fig0, use_container_width=False)

    if temp is not None:
        st.write(temp)